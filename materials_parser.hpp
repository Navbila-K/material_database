// Main header for the lightweight XML parser and material pretty-printer.
#ifndef MATERIALS_PARSER_HPP
#define MATERIALS_PARSER_HPP


#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

// Debug toggle — enables verbose XML parsing logs when diagnosing issues.
namespace materials {

#ifndef DEBUG_XML_EN
#define DEBUG_XML_EN 1
#endif

#if DEBUG_XML_EN
#define DBG(x) do { std::cerr << "[DEBUG] " << x << "\n"; } while(0)
#else
#define DBG(x) do {} while(0)
#endif

// Utility: returns a trimmed copy of the input string (non-destructive).
static inline std::string trim_copy(const std::string &s) {
    size_t a = 0;
    while (a < s.size() && std::isspace((unsigned char)s[a])) ++a;
    size_t b = s.size();
    while (b > a && std::isspace((unsigned char)s[b-1])) --b;
    return s.substr(a, b - a);
}

// Converts XML escape sequences (&amp;, &lt;, etc.) back to their literal characters.
static inline std::string xml_unescape(const std::string &s) {
    std::string out;
    out.reserve(s.size());
    for (size_t i = 0; i < s.size(); ++i) {
        if (s[i] == '&') {
            if (s.compare(i,6,"&quot;")==0) { out.push_back('"'); i += 5; }
            else if (s.compare(i,6,"&apos;")==0) { out.push_back('\''); i += 5; }
            else if (s.compare(i,5,"&amp;")==0) { out.push_back('&'); i += 4; }
            else if (s.compare(i,4,"&lt;")==0) { out.push_back('<'); i += 3; }
            else if (s.compare(i,4,"&gt;")==0) { out.push_back('>'); i += 3; }
            else { out.push_back('&'); }
        } else out.push_back(s[i]);
    }
    return out;
}


static inline std::string attr_safe(const std::map<std::string,std::string> &m, const std::string &k) {
    auto it = m.find(k);
    return (it == m.end() ? std::string() : it->second);
}

static inline bool is_name_char(char c) {
    return std::isalnum((unsigned char)c) || c == '_' || c == ':' || c == '-' || c == '.';
}

static inline std::string humanize_tag(const std::string &tag) {
    if (tag.empty()) return tag;
    std::string out;
    out.reserve(tag.size()*2);
    bool last_upper = false;
    for (size_t i=0;i<tag.size();++i) {
        char c = tag[i];
        if (c=='_' || c=='-') { out.push_back(' '); last_upper = true; continue; }
        if (i>0 && std::isupper((unsigned char)c) && !last_upper) { out.push_back(' '); out.push_back(c); last_upper = true; continue; }
        out.push_back(c);
        last_upper = std::isupper((unsigned char)c);
    }
    std::string t = trim_copy(out);
    std::string r; r.reserve(t.size());
    bool was_space = false;
    for (char ch : t) {
        if (std::isspace((unsigned char)ch)) { if (!was_space) { r.push_back(' '); was_space = true; } }
        else { r.push_back(ch); was_space = false; }
    }
    if (!r.empty()) r[0] = std::toupper((unsigned char)r[0]);
    return r;
}

static inline std::string indent_str(int n) { return std::string(n, ' '); }

// Basic XML node representation: tag name, attributes, inner text, and ordered children.
struct XmlNode {
    std::string name;
    std::string inner_text;                      
    std::map<std::string,std::string> attrs;     
    std::vector<XmlNode> children;               

    std::optional<std::string> attr(const std::string &k) const {
        auto it = attrs.find(k);
        if (it == attrs.end()) return std::nullopt;
        return it->second;
    }

    const XmlNode* find_child(const std::string &tag) const {
        for (const auto &c : children) if (c.name == tag) return &c;
        return nullptr;
    }

    std::vector<const XmlNode*> find_children(const std::string &tag) const {
        std::vector<const XmlNode*> out;
        for (const auto &c : children) if (c.name == tag) out.push_back(&c);
        return out;
    }
};

// Finds the matching '>' for an opening tag, correctly skipping quoted sections.
static size_t find_tag_end(const std::string &s, size_t pos) {
    bool in_quote = false; char q = 0;
    for (size_t i = pos; i < s.size(); ++i) {
        char ch = s[i];
        if (!in_quote && (ch == '"' || ch == '\'')) { in_quote = true; q = ch; continue; }
        if (in_quote && ch == q) { in_quote = false; q = 0; continue; }
        if (!in_quote && ch == '>') return i;
    }
    return std::string::npos;
}

// Parses attributes inside a tag into a key→value map, handling quoted and unquoted values.
static std::map<std::string,std::string> parse_attributes_blob(const std::string &blob) {
    std::map<std::string,std::string> out;
    size_t i = 0;
    while (i < blob.size()) {
        while (i < blob.size() && std::isspace((unsigned char)blob[i])) ++i;
        if (i >= blob.size()) break;
        size_t name_start = i;
        while (i < blob.size() && is_name_char(blob[i])) ++i;
        if (i == name_start) { ++i; continue; }
        std::string name = blob.substr(name_start, i - name_start);
        while (i < blob.size() && std::isspace((unsigned char)blob[i])) ++i;
        if (i >= blob.size() || blob[i] != '=') { out[name] = ""; continue; }
        ++i; while (i < blob.size() && std::isspace((unsigned char)blob[i])) ++i;
        if (i >= blob.size()) { out[name] = ""; break; }
        char quote = 0;
        if (blob[i] == '"' || blob[i] == '\'') { quote = blob[i]; ++i; }
        size_t val_start = i;
        if (quote) {
            size_t val_end = blob.find(quote, i);
            if (val_end == std::string::npos) { out[name] = xml_unescape(blob.substr(val_start)); break; }
            out[name] = xml_unescape(blob.substr(val_start, val_end - val_start));
            i = val_end + 1;
        } else {
            while (i < blob.size() && !std::isspace((unsigned char)blob[i])) ++i;
            out[name] = xml_unescape(blob.substr(val_start, i - val_start));
        }
    }
    return out;
}

// Reads an opening XML tag, extracting the tag name and raw attribute content.
static bool read_opening_tag(const std::string &s, size_t pos, std::string &out_name, std::string &out_attr_blob, size_t &tag_start, size_t &tag_end) {
    tag_start = pos;
    if (pos >= s.size() || s[pos] != '<') return false;
    size_t gt = find_tag_end(s, pos);
    if (gt == std::string::npos) { DBG("read_opening_tag: couldn't find '>' from pos=" << pos); return false; }
    std::string header = s.substr(pos+1, gt - (pos+1));
    size_t idx = 0;
    while (idx < header.size() && std::isspace((unsigned char)header[idx])) ++idx;
    if (idx < header.size() && (header[idx] == '?' || header[idx] == '!')) { DBG("read_opening_tag: skipped special tag at pos=" << pos << " header='" << header << "'"); return false; }
    size_t ns = idx;
    while (ns < header.size() && is_name_char(header[ns])) ++ns;
    if (ns == idx) { DBG("read_opening_tag: no name found in header='" << header << "'"); return false; }
    out_name = header.substr(idx, ns - idx);
    std::string rest = header.substr(ns);
    size_t start = 0;
    while (start < rest.size() && std::isspace((unsigned char)rest[start])) ++start;
    size_t end = rest.size();
    while (end > start && std::isspace((unsigned char)rest[end-1])) --end;
    std::string mid = (end > start) ? rest.substr(start, end - start) : std::string();
    if (!mid.empty() && mid.back() == '/') {
        mid.pop_back();
        while (!mid.empty() && std::isspace((unsigned char)mid.back())) mid.pop_back();
    }
    out_attr_blob = mid;
    tag_end = gt;
    DBG("read_opening_tag: name='" << out_name << "' attr_blob='" << out_attr_blob << "' tag_start=" << tag_start << " tag_end=" << tag_end);
    return true;
}

// Locates the corresponding closing tag, accounting for nested elements of the same name.
static bool find_closing_tag(const std::string &s, const std::string &tag, size_t tag_start, size_t &close_pos, size_t &inner_start, size_t &inner_end) {
    size_t open_end = find_tag_end(s, tag_start);
    if (open_end == std::string::npos) { DBG("find_closing_tag: open_end not found"); return false; }
    inner_start = open_end + 1;
    bool self_closing = false;
    for (size_t i = open_end; i > tag_start; --i) {
        if (s[i-1] == '/') { self_closing = true; break; }
        if (!std::isspace((unsigned char)s[i-1])) break;
    }
    if (self_closing) { close_pos = open_end; inner_end = open_end; DBG("find_closing_tag: self-closing tag '" << tag << "'"); return true; }
    size_t pos = inner_start;
    int depth = 1;
    while (pos < s.size()) {
        size_t lt = s.find('<', pos);
        if (lt == std::string::npos) break;
        if (s.compare(lt, 4, "<!--") == 0) {
            size_t q = s.find("-->", lt+4);
            pos = (q == std::string::npos) ? s.size() : q + 3;
            continue;
        }
        if (s.compare(lt,2,"<?") == 0) {
            size_t q = s.find("?>", lt+2);
            pos = (q == std::string::npos) ? s.size() : q + 2;
            continue;
        }
        if (lt+1 < s.size() && s[lt+1] == '/') {
            size_t gt = find_tag_end(s, lt);
            if (gt == std::string::npos) return false;
            size_t nm_start = lt + 2;
            while (nm_start < gt && std::isspace((unsigned char)s[nm_start])) ++nm_start;
            size_t nm_end = nm_start;
            while (nm_end < gt && is_name_char(s[nm_end])) ++nm_end;
            std::string cname = s.substr(nm_start, nm_end - nm_start);
            if (cname == tag) {
                --depth;
                if (depth == 0) { close_pos = lt; inner_end = lt; DBG("find_closing_tag: found closing for '" << tag << "' at pos=" << lt); return true; }
            }
            pos = gt + 1;
            continue;
        } else {
            size_t gt = find_tag_end(s, lt);
            if (gt == std::string::npos) return false;
            size_t nm_start = lt + 1;
            while (nm_start < gt && std::isspace((unsigned char)s[nm_start])) ++nm_start;
            if (nm_start < gt && (s[nm_start] == '?' || s[nm_start] == '!')) { pos = gt + 1; continue; }
            size_t nm_end = nm_start;
            while (nm_end < gt && is_name_char(s[nm_end])) ++nm_end;
            if (nm_end > nm_start) {
                std::string cname = s.substr(nm_start, nm_end - nm_start);
                if (cname == tag) ++depth;
            }
            pos = gt + 1;
            continue;
        }
    }
    DBG("find_closing_tag: failed to find closing for tag '" << tag << "'");
    return false;
}

// Recursively builds an XmlNode and its subtree starting from the current parse position.
static bool build_node_from_string(const std::string &s, size_t &pos_global, XmlNode &out) {
    DBG("build_node_from_string: starting at pos_global=" << pos_global);
    std::string tag, attr_blob;
    size_t tag_start = 0, tag_end = 0;
    if (!read_opening_tag(s, pos_global, tag, attr_blob, tag_start, tag_end)) {
        DBG("build_node_from_string: read_opening_tag failed at pos=" << pos_global);
        return false;
    }
    DBG("build_node_from_string: opening tag '" << tag << "' at " << tag_start << "-" << tag_end);
    out.name = tag;
    out.attrs = parse_attributes_blob(attr_blob);
    size_t close_pos = 0, inner_start = 0, inner_end = 0;
    if (!find_closing_tag(s, tag, tag_start, close_pos, inner_start, inner_end)) {
        size_t nextlt = s.find('<', tag_end+1);
        if (nextlt == std::string::npos) nextlt = s.size();
        out.inner_text = trim_copy(xml_unescape(s.substr(tag_end+1, nextlt - (tag_end+1))));
        pos_global = nextlt;
        DBG("build_node_from_string: no closing tag found for '" << tag << "', treated as text-only. pos now " << pos_global);
        return true;
    }
    if (inner_start >= inner_end) {
        out.inner_text.clear();
        size_t gt = find_tag_end(s, close_pos);
        pos_global = (gt == std::string::npos) ? close_pos : gt + 1;
        DBG("build_node_from_string: empty inner for '" << tag << "'. pos now " << pos_global);
        return true;
    }
    std::string inner = s.substr(inner_start, inner_end - inner_start);
    out.inner_text.clear();
    size_t ipos = 0;
    while (ipos < inner.size()) {
        while (ipos < inner.size() && std::isspace((unsigned char)inner[ipos])) ++ipos;
        if (ipos >= inner.size()) break;
        if (inner.compare(ipos, 4, "<!--") == 0) {
            size_t q = inner.find("-->", ipos+4);
            if (q == std::string::npos) break;
            DBG("build_node_from_string: skipping inner comment at pos " << (inner_start + ipos));
            ipos = q + 3;
            continue;
        }
        if (inner[ipos] != '<') {
            size_t nl = inner.find('<', ipos);
            if (nl == std::string::npos) nl = inner.size();
            std::string seg = trim_copy(inner.substr(ipos, nl - ipos));
            if (!seg.empty()) {
                if (!out.inner_text.empty()) out.inner_text += " ";
                out.inner_text += xml_unescape(seg);
            }
            ipos = nl;
            continue;
        }
        size_t global_pos = inner_start + ipos;
        XmlNode child;
        if (!build_node_from_string(s, global_pos, child)) {
            DBG("build_node_from_string: child parse failed at global_pos=" << global_pos << " (inside parent '" << tag << "') -- advancing one char to avoid infinite loop");
            ++ipos;
            continue;
        }
        DBG("build_node_from_string: parsed child '" << child.name << "' of parent '" << tag << "'");
        out.children.push_back(std::move(child));
        ipos = global_pos - inner_start;
    }
    size_t gt = find_tag_end(s, close_pos);
    pos_global = (gt == std::string::npos) ? close_pos : gt + 1;
    out.inner_text = trim_copy(out.inner_text);
    DBG("build_node_from_string: completed node '" << out.name << "' with " << out.children.size() << " children; pos now " << pos_global);
    return true;
}

// High-level parser: loads XML from file, removes noise (BOM, comments, declarations), and builds the node tree.
struct SimpleXmlParser {
    // Load entire XML file into a contiguous string buffer for efficient parsing.
    XmlNode loadFromFile(const std::string &path) {
        XmlNode root;
        std::ifstream ifs(path, std::ios::binary);
        if (!ifs) throw std::runtime_error("failed to open XML file: " + path);
        std::string s((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
        DBG("Loaded XML file '" << path << "' length=" << s.size());
        if (s.size() >= 3 && (unsigned char)s[0] == 0xEF && (unsigned char)s[1] == 0xBB && (unsigned char)s[2] == 0xBF) {
            DBG("Detected UTF-8 BOM at file start; removing 3 bytes");
            s.erase(0,3);
        }
        while (true) {
            size_t p = s.find("<?");
            if (p == std::string::npos) break;
            size_t q = s.find("?>", p+2);
            if (q == std::string::npos) { DBG("Unterminated XML declaration starting at " << p << " -- aborting strip"); break; }
            DBG("Removing XML declaration at pos " << p << " .. " << q+1);
            s.erase(p, q - p + 2);
        }
        while (true) {
            size_t p = s.find("<!--");
            if (p == std::string::npos) break;
            size_t q = s.find("-->", p+4);
            if (q == std::string::npos) { DBG("Unterminated comment starting at " << p << " -- aborting strip"); break; }
            DBG("Removing comment at pos " << p << " .. " << q+2);
            s.erase(p, q - p + 3);
        }
        DBG("After cleanup length=" << s.size());
        size_t pos = s.find('<');
        DBG("First '<' in cleaned file at index " << pos);
        if (pos == std::string::npos) throw std::runtime_error("XML error: no opening '<' found after cleanup");
        bool found = false;
        while (pos < s.size()) {
            if (s.compare(pos, 4, "<!--") == 0) {
                size_t q = s.find("-->", pos+4); if (q==std::string::npos) break; pos = q+3; continue;
            }
            if (s.compare(pos,2,"<?") == 0) { size_t q = s.find("?>", pos+2); if (q==std::string::npos) break; pos = q+2; continue; }
            if (s.compare(pos,2,"<!") == 0) {
                size_t q = s.find('>', pos+2); if (q==std::string::npos) break; pos = q+1; continue;
            }
            std::string nm; std::string blob; size_t ts, te;
            if (read_opening_tag(s, pos, nm, blob, ts, te)) {
                DBG("Candidate root opening tag found: '" << nm << "' at pos " << pos);
                found = true;
                break;
            } else {
                ++pos;
            }
        }
        if (!found) throw std::runtime_error("failed to find a root opening tag in the file");
        size_t posGlobal = pos;
        if (!build_node_from_string(s, posGlobal, root)) {
            DBG("build_node_from_string failed for root start pos=" << pos);
            throw std::runtime_error("failed to parse root element");
        }
        DBG("Parsed root node: <" << root.name << "> with " << root.children.size() << " top-level children");
        return root;
    }
};

struct MaterialDescriptor {
    XmlNode root; 
};

static MaterialDescriptor parseMaterialFile(const std::string &path) {
    SimpleXmlParser p;
    XmlNode root = p.loadFromFile(path);
    if (root.name.empty()) throw std::runtime_error("empty XML root");
    MaterialDescriptor md;
    md.root = std::move(root);
    return md;
}

static void write_pretty_text_recursive(std::ostream &ofs, const XmlNode &node, int indent);

static void print_entries_block(std::ostream &ofs, const XmlNode &parent, int indent) {
    auto entries = parent.find_children("Entry");
    if (!entries.empty()) {
        std::string unit = attr_safe(parent.attrs, "unit");
        for (const XmlNode* e : entries) {
            std::string val = e->inner_text;
            std::string ref = attr_safe(e->attrs, "ref");
            std::string eunit = attr_safe(e->attrs, "unit");
            if (!val.empty()) {
                ofs << indent_str(indent) << val;
                if (!ref.empty()) ofs << " (" << ref << ")";
                if (!eunit.empty() && eunit != unit) ofs << " [" << eunit << "]";
                ofs << "\n";
            } else {
                ofs << indent_str(indent) << "\n";
            }
        }
    } else {
        // If the parent has no <Entry> children but contains text, print the text directly with indentation.
        if (!parent.inner_text.empty()) {
            ofs << indent_str(indent) << parent.inner_text << "\n";
        } else {
            // Walk through child tags and print nested entry groups or delegate to recursive formatting.
            for (const XmlNode &c : parent.children) {
                auto entries2 = c.find_children("Entry");
                if (!entries2.empty()) {
                    std::string header = humanize_tag(c.name);
                    std::string unit = attr_safe(c.attrs, "unit");
                    ofs << indent_str(indent) << header;
                    if (!unit.empty()) ofs << " (" << unit << ")";
                    ofs << "\n";
                    print_entries_block(ofs, c, indent + 4);
                } else if (!c.children.empty()) {
                    std::string header = humanize_tag(c.name);
                    ofs << indent_str(indent) << header << "\n";
                    write_pretty_text_recursive(ofs, c, indent+4);
                } else {
                    if (!c.inner_text.empty()) {
                        ofs << indent_str(indent) << humanize_tag(c.name);
                        if (!c.attrs.empty()) {
                            if (c.attrs.count("unit")) ofs << " (" << c.attrs.at("unit") << ")";
                            if (c.attrs.count("ref")) ofs << " (" << c.attrs.at("ref") << ")";
                        }
                        ofs << " : " << c.inner_text << "\n";
                    } else {
                        ofs << indent_str(indent) << humanize_tag(c.name);
                        if (!c.attrs.empty()) {
                            if (c.attrs.count("unit")) ofs << " (" << c.attrs.at("unit") << ")";
                            if (c.attrs.count("ref")) ofs << " (" << c.attrs.at("ref") << ")";
                        }
                        ofs << " :\n";
                    }
                }
            }
        }
    }
}

static void write_pretty_text_recursive(std::ostream &ofs, const XmlNode &node, int indent) {
    auto entries = node.find_children("Entry");
    // If this node directly holds <Entry> elements, print them as a simple value block.
    if (!entries.empty()) {
        print_entries_block(ofs, node, indent);
        return;
    }

    // <Row> elements represent structured EOS/table rows; format them with clearer section labeling.
    if (node.name == "Row") {
        std::string idx = attr_safe(node.attrs, "index");
        const XmlNode* kindNode = node.find_child("Kind");
        std::string kind = kindNode ? kindNode->inner_text : std::string();
        std::ostringstream hdr;
        hdr << "ROW";
        if (!idx.empty()) hdr << " " << idx;
        hdr << " — ";
        if (!kind.empty()) hdr << kind; else hdr << humanize_tag(node.name);
        ofs << indent_str(indent) << hdr.str() << "\n";
        for (const XmlNode &c : node.children) {
            if (c.name == "Kind") {
                ofs << indent_str(indent + 4) << "Kind";
                if (!c.attrs.empty() && c.attrs.count("ref")) ofs << " (" << c.attrs.at("ref") << ")";
                ofs << " : " << c.inner_text << "\n";
                continue;
            }
            auto e2 = c.find_children("Entry");
            if (!e2.empty()) {
                std::string label = humanize_tag(c.name);
                std::string unit = attr_safe(c.attrs, "unit");
                ofs << indent_str(indent+4) << label;
                if (!unit.empty()) ofs << " – " << unit;
                ofs << "\n";
                print_entries_block(ofs, c, indent+8);
                continue;
            }
            if (!c.children.empty()) {
                std::string subname = humanize_tag(c.name);
                ofs << indent_str(indent+4) << subname << "\n";
                write_pretty_text_recursive(ofs, c, indent+8);
                continue;
            }
            if (!c.inner_text.empty()) {
                ofs << indent_str(indent+4) << humanize_tag(c.name);
                if (!c.attrs.empty()) {
                    if (c.attrs.count("unit")) ofs << " – " << c.attrs.at("unit");
                    if (c.attrs.count("ref")) ofs << " (" << c.attrs.at("ref") << ")";
                }
                ofs << " : " << c.inner_text << "\n";
            } else {
                ofs << indent_str(indent+4) << humanize_tag(c.name);
                if (!c.attrs.empty()) {
                    if (c.attrs.count("unit")) ofs << " – " << c.attrs.at("unit");
                    if (c.attrs.count("ref")) ofs << " (" << c.attrs.at("ref") << ")";
                }
                ofs << " :\n";
            }
        }
        ofs << "\n";
        return;
    }
    // For elements inside a Row that contain multiple <Entry> values, print them as labeled sub-blocks.
    for (const XmlNode &c : node.children) {
        if (c.name == "Metadata") continue;
        // Category nodes introduce a new high-level section in the output, so print header lines before recursion.
        if (c.name == "Category") {
            for (const XmlNode &sub : c.children) {
                std::string header = humanize_tag(sub.name);
                ofs << indent_str(indent) << "--------------------------------------------------------------------\n";
                ofs << indent_str(indent) << header << "\n";
                ofs << indent_str(indent) << "--------------------------------------------------------------------\n\n";
                write_pretty_text_recursive(ofs, sub, indent+4);
            }
            continue;
        }

        // Regular nested nodes: print a titled block and recursively format all child elements.
        auto e = c.find_children("Entry");
        if (!e.empty()) {
            std::string label = humanize_tag(c.name);
            if (!c.attrs.empty() && c.attrs.count("unit")) {
                ofs << indent_str(indent) << label << " (" << c.attrs.at("unit") << ")\n";
            } else {
                ofs << indent_str(indent) << label << "\n";
            }
            print_entries_block(ofs, c, indent + 4);
            ofs << "\n";
            continue;
        }

        if (!c.children.empty()) {
            std::string header = humanize_tag(c.name);
            ofs << indent_str(indent) << header << "\n";
            write_pretty_text_recursive(ofs, c, indent+4);
            ofs << "\n";
            continue;
        }

        if (!c.inner_text.empty() || !c.attrs.empty()) {
            ofs << indent_str(indent) << humanize_tag(c.name);
            if (!c.attrs.empty()) {
                if (c.attrs.count("unit")) ofs << " – " << c.attrs.at("unit");
                if (c.attrs.count("ref")) ofs << " (" << c.attrs.at("ref") << ")";
            }
            if (!c.inner_text.empty()) ofs << " : " << c.inner_text;
            ofs << "\n";
        }
    }
}

// Begin writing the formatted material file with a standardized title header.
static void writeDescriptorAsText(const MaterialDescriptor &md, const std::string &out_path) {
    std::ofstream ofs(out_path);
    if (!ofs) throw std::runtime_error("failed to open text output file: " + out_path);

    ofs << "====================================================================\n";
    ofs << "                           MATERIAL DATA\n";
    ofs << "====================================================================\n\n";

    // Output the metadata section first, preserving ordering and optional meaning attributes.
    const XmlNode *meta = md.root.find_child("Metadata");
    if (meta) {
        ofs << "--------------------------------------------------------------------\n";
        ofs << "METADATA\n";
        ofs << "--------------------------------------------------------------------\n\n";
        for (const XmlNode &m : meta->children) {
            if (!m.inner_text.empty()) {
                ofs << "    " << humanize_tag(m.name);
                if (!m.attrs.empty()) {
                    if (m.attrs.count("meaning")) ofs << " (" << m.attrs.at("meaning") << ")";
                }
                ofs << " : " << m.inner_text << "\n";
            } else {
                ofs << "    " << humanize_tag(m.name);
                if (!m.attrs.empty()) {
                    if (m.attrs.count("meaning")) ofs << " (" << m.attrs.at("meaning") << ")";
                }
                ofs << " :\n";
            }
        }
        ofs << "\n";
    }

    // Print each top-level category or element, skipping Metadata since it was handled earlier.
    for (const XmlNode &top : md.root.children) {
        if (top.name == "Metadata") continue;
        if (top.name == "Category") {
            for (const XmlNode &sub : top.children) {
                std::string header = humanize_tag(sub.name);
                ofs << "--------------------------------------------------------------------\n";
                ofs << header << "\n";
                ofs << "--------------------------------------------------------------------\n\n";
                write_pretty_text_recursive(ofs, sub, 0);
            }
            continue;
        }
        ofs << "--------------------------------------------------------------------\n";
        ofs << humanize_tag(top.name) << "\n";
        ofs << "--------------------------------------------------------------------\n\n";
        write_pretty_text_recursive(ofs, top, 0);
    }

    // Closing footer to clearly mark the end of the formatted material file.
    ofs << "====================================================================\n";
    ofs << "                         END OF MATERIAL FILE\n";
    ofs << "====================================================================\n";
}

// Returns the inner text of a named child, or std::nullopt if the child doesn't exist.
static std::optional<std::string> get_child_text(const XmlNode &parent, const std::string &child_name) {
    const XmlNode* c = parent.find_child(child_name);
    if (!c) return std::nullopt;
    return c->inner_text;
}

// Safely retrieves an attribute value by key, returning std::nullopt if absent.
static std::optional<std::string> get_attr_safe(const XmlNode &n, const std::string &k) {
    auto it = n.attrs.find(k);
    if (it == n.attrs.end()) return std::nullopt;
    return it->second;
}

}

#endif