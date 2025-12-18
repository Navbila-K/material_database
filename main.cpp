// main.cpp
// Simple command-line browser for Material XML files using the custom XML parser.
// Requires: materials_parser.hpp in same folder (C++17)
// Compile: g++ -std=c++17 main.cpp -o mat_browser

#include <iostream>
#include <string>
#include <array>
#include <vector>
#include <filesystem>
#include <limits>
#include <algorithm>
#include <cstdint>
#include <sstream>
#include <cctype>
#include "materials_parser.hpp"

using namespace materials;
namespace fs = std::filesystem;


// Simulator version and minimum XML version checks for compatibility control.
#define SIM_VERSION "0.0.0"
#define MIN_SUPPORTED_VERSION "0.0.0"

// Reads a full user input line and trims surrounding whitespace.
static std::string readline_trim() {
    std::string s;
    std::getline(std::cin, s);
    size_t a = 0;
    while (a < s.size() && std::isspace((unsigned char)s[a])) ++a;
    size_t b = s.size();
    while (b > a && std::isspace((unsigned char)s[b-1])) --b;
    return s.substr(a, b - a);
}

// Displays a prompt, reads a number, and returns -1 for invalid input.
static int ask_choice(const std::string &prompt) {
    std::cout << prompt;
    std::string line = readline_trim();
    if (line.empty()) return -1;
    try { return std::stoi(line); } catch (...) { return -1; }
}

// Scans the current directory for .xml files and returns a sorted list.
static std::vector<fs::path> find_xml_files_in_cwd() {
    std::vector<fs::path> out;
    for (auto &entry : fs::directory_iterator(fs::current_path())) {
        if (!entry.is_regular_file()) continue;
        auto p = entry.path();
        auto ext = p.extension().string();
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        if (ext == ".xml") out.push_back(p);
    }
    std::sort(out.begin(), out.end());
    return out;
}

// Prints a numbered list of XML files for user selection.
static void print_files_list(const std::vector<fs::path> &files) {
    for (size_t i=0;i<files.size();++i) std::cout << "  " << (i+1) << ". " << files[i].filename().string() << "\n";
}

// FNV-1a hash used to compute the expected checksum for <Version>.
static uint32_t fnv1a(const std::string &s) {
    uint32_t hash = 0x811C9DC5u;
    for (unsigned char c : s) {
        hash ^= c;
        hash *= 16777619u;
    }
    return hash;
}

// Converts a 32-bit integer into an 8-character uppercase hex string.
static std::string to_hex8(uint32_t v) {
    char buf[16];
    std::sprintf(buf, "%08X", v);
    return std::string(buf);
}

// Parses semantic version strings into {major, minor, patch}.
static bool parse_semver(const std::string &s, std::array<int,3> &out) {
    out = {0,0,0};
    std::string t = s;
    size_t a = 0; while (a < t.size() && std::isspace((unsigned char)t[a])) ++a;
    size_t b = t.size(); while (b > a && std::isspace((unsigned char)t[b-1])) --b;
    if (b <= a) return false;
    t = t.substr(a, b-a);
    std::vector<int> parts;
    std::stringstream ss(t);
    std::string item;
    while (std::getline(ss, item, '.')) {
        if (item.empty()) { parts.push_back(0); continue; }
        bool ok = true;
        for (char c : item) if (!std::isdigit((unsigned char)c)) { ok = false; break; }
        if (!ok) return false;
        try { parts.push_back(std::stoi(item)); } catch (...) { return false; }
    }
    for (size_t i=0;i<3 && i<parts.size();++i) out[i] = parts[i];
    return true;
}

// Standard semantic version comparison: -1, 0, +1.
static int semver_compare(const std::array<int,3> &a, const std::array<int,3> &b) {
    for (int i=0;i<3;++i) {
        if (a[i] < b[i]) return -1;
        if (a[i] > b[i]) return +1;
    }
    return 0;
}

// Validates that the XML document has all mandatory sections and tags.
static bool has_required_structure(const XmlNode &root, std::string &err) {
    if (root.name != "Material") { err = "Root element must be <Material>"; return false; }
    const XmlNode *meta = root.find_child("Metadata"); if (!meta) { err = "Missing <Metadata>"; return false; }
    const char* metas[] = {"Id","Name","Version"};
    for (auto t : metas) { if (!meta->find_child(t)) { err = std::string("Missing <") + t + "> in <Metadata>"; return false; } }
    const XmlNode *cat = root.find_child("Category"); if (!cat) { err = "Missing <Category>"; return false; }
    if (!cat->find_child("Property")) { err = "Missing <Property> inside <Category>"; return false; }
    if (!cat->find_child("Model"))    { err = "Missing <Model>    inside <Category>"; return false; }
    return true;
}

// Validates <Id>, <Version>, checksum correctness, and semantic version compatibility.
static bool validate_version_checksum_and_range(const XmlNode &root, const std::string &min_supported_ver, const std::string &sim_ver, std::string &err_out, std::string &out_version_str) {
    // Extract and verify <Id> and <Version> fields from <Metadata>.
    const XmlNode *meta = root.find_child("Metadata");
    if (!meta) { err_out = "Missing <Metadata>"; return false; }
    const XmlNode *idNode = meta->find_child("Id");
    const XmlNode *verNode = meta->find_child("Version");
    if (!idNode) { err_out = "Missing <Id>"; return false; }
    if (!verNode) { err_out = "Missing <Version>"; return false; }

    std::string id = idNode->inner_text;
    std::string verfield = verNode->inner_text;
    if (id.empty()) { err_out = "<Id> is empty"; return false; }
    if (verfield.empty()) { err_out = "<Version> is empty"; return false; }

    size_t dash = verfield.rfind('-');
    // Parse MAJOR.MINOR.PATCH and checksum from Version string.
    if (dash == std::string::npos) { err_out = "<Version> must be in format MAJOR.MINOR.PATCH-CHECKSUM (e.g. 1.0.0-10C18EDC)"; return false; }
    std::string verpart = verfield.substr(0, dash);
    std::string checksum_part = verfield.substr(dash + 1);

    if (checksum_part.size() != 8) { err_out = "Checksum part must have 8 hex characters"; return false; }
    for (char ch : checksum_part) {
        if (!std::isxdigit((unsigned char)ch)) { err_out = "Checksum contains non-hex characters"; return false; }
    }

    // Validate checksum by recomputing FNV-1a hash of the Id field.
    std::string expected = to_hex8(fnv1a(id));
    auto up = [](std::string s){ for (char &c: s) c = (char)std::toupper((unsigned char)c); return s; };
    if (up(checksum_part) != up(expected)) {
        err_out = "Checksum mismatch: expected " + expected + " for Id='" + id + "' but Version has " + checksum_part;
        return false;
    }

    // Parse and compare semantic version numbers against required ranges.
    std::array<int,3> xmlv, minv, simv;
    if (!parse_semver(verpart, xmlv)) { err_out = "Failed to parse semantic version part: '" + verpart + "'"; return false; }
    if (!parse_semver(min_supported_ver, minv)) { err_out = "Internal error: bad MIN_SUPPORTED_VERSION macro"; return false; }
    if (!parse_semver(sim_ver, simv)) { err_out = "Internal error: bad SIM_VERSION macro"; return false; }

    if (semver_compare(xmlv, minv) < 0) {
        err_out = "Material XML version '" + verpart + "' is too old (minimum supported is " + min_supported_ver + ")";
        return false;
    }
    if (semver_compare(xmlv, simv) > 0) {
        err_out = "Material XML version '" + verpart + "' is newer than simulator (" + sim_ver + "). Update simulator or use an older XML.";
        return false;
    }

    out_version_str = verpart;
    return true;
}

// Finds a <Row> element inside an EOS model by matching its index attribute.
static const XmlNode* find_eos_row_by_index(const XmlNode &eos, const std::string &indexValue) {
    auto rows = eos.find_children("Row");
    for (const XmlNode* r : rows) {
        auto idx = r->attr("index");
        if (idx && *idx == indexValue) return r;
    }
    return nullptr;
}

// Optional-returning version of attr_safe: returns std::nullopt if attribute missing.
static std::optional<std::string> attr_safe_opt(const std::map<std::string,std::string> &m, const std::string &k) {
    auto it = m.find(k);
    if (it==m.end()) return std::nullopt;
    return it->second;
}

// Displays metadata fields in a simple readable format.
static void show_metadata(const XmlNode &root) {
    const XmlNode* meta = root.find_child("Metadata");
    if (!meta) { std::cout << "No <Metadata> section found.\n"; return; }
    std::cout << "---- METADATA ----\n";
    for (const auto &m : meta->children) {
        std::cout << m.name << " : " << (m.inner_text.empty() ? "(empty)" : m.inner_text);
        if (!m.attrs.empty()) {
            if (m.attrs.count("meaning")) std::cout << " (" << m.attrs.at("meaning") << ")";
        }
        std::cout << "\n";
    }
    std::cout << "------------------\n";
}

// Lists all child fields of a node, showing values/units/refs when available.
static void show_node_children_as_fields(const XmlNode &node) {
    if (node.children.empty()) { std::cout << "(no children)\n"; return; }
    for (const auto &c : node.children) {
        auto entries = c.find_children("Entry");
        if (!entries.empty()) {
            std::cout << c.name;
            if (c.attrs.count("unit")) std::cout << " [unit=" << c.attrs.at("unit") << "]";
            std::cout << ":\n";
            int idx = 1;
            for (const XmlNode* e : entries) {
                std::string val = e->inner_text.empty() ? "(empty)" : e->inner_text;
                std::string ref = attr_safe(e->attrs, "ref");
                std::string unit = attr_safe(e->attrs, "unit");
                std::cout << "   Entry " << idx++ << ": " << val;
                if (!unit.empty()) std::cout << " [unit=" << unit << "]";
                if (!ref.empty())  std::cout << " (ref=" << ref << ")";
                std::cout << "\n";
            }
            continue;
        }
        std::string val  = c.inner_text.empty() ? "(empty)" : c.inner_text;
        std::string ref  = attr_safe(c.attrs, "ref");
        std::string unit = attr_safe(c.attrs, "unit");
        std::cout << c.name << " : " << val;
        if (!unit.empty()) std::cout << " [unit=" << unit << "]";
        if (!ref.empty())  std::cout << " (ref=" << ref << ")";
        std::cout << "\n";
    }
}

// UI helper: lets the user pick a child node by index, or return to previous menu.
static const XmlNode* choose_child_by_number(const XmlNode &parent) {
    if (parent.children.empty()) { std::cout << "No children available.\n"; return nullptr; }
    for (size_t i=0;i<parent.children.size();++i) std::cout << "  " << (i+1) << ". " << parent.children[i].name << "\n";
    std::cout << "  0. Back\n";
    int ch = ask_choice("Choose child number: ");
    if (ch <= 0) return nullptr;
    if (static_cast<size_t>(ch) > parent.children.size()) { std::cout << "Invalid selection.\n"; return nullptr; }
    return &parent.children[ch-1];
}

// Shows detailed information about a selected XML node with mode-based inspection.
static void show_child_detail(const XmlNode &child) {
    std::cout << "\nSelected: <" << child.name << ">\n";

    // MODE 1: Node contains multiple <Entry> elements → allow selective inspection.
    auto entries = child.find_children("Entry");
    if (!entries.empty()) {
        std::cout << "\nThis field has multiple entries. Choose what to show:\n";
        std::cout << "  1. Show values\n";
        std::cout << "  2. Show units\n";
        std::cout << "  3. Show refs\n";
        std::cout << "  4. Show all\n";
        std::cout << "  0. Back\n";

        int c = ask_choice("Choose: ");
        if (c == 0) return;

        int i = 1;
        for (const XmlNode* e : entries) {
            std::string val  = e->inner_text.empty() ? "(empty)" : e->inner_text;
            std::string unit = attr_safe(e->attrs, "unit");
            std::string ref  = attr_safe(e->attrs, "ref");

            std::cout << "Entry " << i++ << ": ";

            switch (c) {
                case 1: std::cout << val; break;
                case 2: std::cout << (unit.empty() ? "(none)" : unit); break;
                case 3: std::cout << (ref.empty() ? "(none)" : ref); break;
                case 4:
                    std::cout << val;
                    if (!unit.empty()) std::cout << " [unit=" << unit << "]";
                    if (!ref.empty())  std::cout << " (ref=" << ref << ")";
                    break;
                default: std::cout << "Invalid";
            }

            std::cout << "\n";
        }

        return;
    }

    // MODE 2: Node is a container → show its subfields and allow drilling deeper.
    if (!child.children.empty()) {
        std::cout << "\nThis section has subfields:\n";
        for (size_t i = 0; i < child.children.size(); ++i) {
            std::cout << "  " << (i + 1) << ". " << child.children[i].name << "\n";
        }
        std::cout << "  0. Back\n";

        int c = ask_choice("Choose field: ");
        if (c <= 0 || c > (int)child.children.size()) return;

        show_child_detail(child.children[c - 1]);
        return;
    }

    // MODE 3: Leaf node → show individual value, unit, ref, or all at once.
    std::cout << "\nOptions:\n";
    std::cout << "  1. Show value\n";
    std::cout << "  2. Show unit\n";
    std::cout << "  3. Show ref\n";
    std::cout << "  4. Show all\n";
    std::cout << "  0. Back\n";

    int c = ask_choice("Choose: ");
    if (c == 0) return;

    std::string val  = child.inner_text.empty() ? "(empty)" : child.inner_text;
    std::string unit = attr_safe(child.attrs, "unit");
    std::string ref  = attr_safe(child.attrs, "ref");

    switch (c) {
        case 1: std::cout << "value: " << val << "\n"; break;
        case 2: std::cout << "unit : " << (unit.empty() ? "(none)" : unit) << "\n"; break;
        case 3: std::cout << "ref  : " << (ref.empty() ? "(none)" : ref) << "\n"; break;
        case 4:
            std::cout << "value: " << val << "\n";
            std::cout << "unit : " << (unit.empty() ? "(none)" : unit) << "\n";
            std::cout << "ref  : " << (ref.empty() ? "(none)" : ref) << "\n";
            break;
        default:
            std::cout << "Invalid option.\n";
    }
}


// Main loop: file selection, loading, validation, and interactive browsing.
int main() {
    try {
        while (true) {
            // Discover and list available XML files in the current directory.
            auto files = find_xml_files_in_cwd();
            if (files.empty()) {
                std::cout << "No .xml files found in current directory (" << fs::current_path() << ").\n";
                return 1;
            }
            std::cout << "XML files found in: " << fs::current_path() << "\n";
            print_files_list(files);
            std::cout << "  0. Exit\n";
            int file_choice = ask_choice("Choose file number to open (0=exit): ");
            if (file_choice == 0) { std::cout << "Exiting.\n"; return 0; }
            if (file_choice < 1 || static_cast<size_t>(file_choice) > files.size()) { std::cout << "Invalid selection.\n"; continue; }

            fs::path chosen = files[file_choice - 1];
            std::cout << "Loading: " << chosen.filename().string() << "\n";

            MaterialDescriptor md;
            try {
                // Parse the chosen XML file using the custom XML parser.
                md = parseMaterialFile(chosen.string());
            } catch (const std::exception &e) {
                std::cerr << "Parse error: " << e.what() << "\n";
                std::cout << "Try another file? (y/n): ";
                std::string r = readline_trim();
                if (!r.empty() && (r[0]=='y' || r[0]=='Y')) continue;
                return 1;
            }

            std::string verr;
            // Validate required structure before allowing interactive browsing.
            if (!has_required_structure(md.root, verr)) {
                std::cerr << "Structure validation failed: " << verr << "\n";
                std::cout << "Try another file? (y/n): ";
                std::string r = readline_trim();
                if (!r.empty() && (r[0]=='y' || r[0]=='Y')) continue;
                return 1;
            }

            std::string verr2;
            std::string xml_verpart;
            // Validate version ranges and checksum integrity.
            if (!validate_version_checksum_and_range(md.root, MIN_SUPPORTED_VERSION, SIM_VERSION, verr2, xml_verpart)) {
                std::cerr << "Version/Checksum validation failed: " << verr2 << "\n";
                std::cout << "Try another file? (y/n): ";
                std::string r = readline_trim();
                if (!r.empty() && (r[0]=='y' || r[0]=='Y')) continue;
                return 1;
            }

            std::cout << "Version OK (" << xml_verpart << "). Checksum OK. Proceeding.\n";

            const XmlNode &root = md.root;
            bool main_exit = false;
            // MAIN MENU: choose between printing to screen or exporting pretty text.
            while (!main_exit) {
                std::cout << "\n===== MAIN MENU =====\n";
                std::cout << "1. Show on screen\n";
                std::cout << "2. Write pretty text to .txt file\n";
                std::cout << "0. Exit\n";
                int choice = ask_choice("Choose option: ");
                if (choice == 0) { std::cout << "Exiting.\n"; return 0; }
                if (choice == 2) {
                    std::string outname = chosen.stem().string() + "_pretty.txt";
                    writeDescriptorAsText(md, outname);
                    std::cout << "Wrote pretty text to: " << outname << "\n";
                    continue;
                }
                if (choice != 1) { std::cout << "Invalid option.\n"; continue; }

                const XmlNode *category = root.find_child("Category");
                const XmlNode *property = nullptr;
                const XmlNode *model = nullptr;

                // Selecting Property / Model sections for deeper browsing.
                if (category) {
                    property = category->find_child("Property");
                    model    = category->find_child("Model");
                }

                bool back_to_main = false;
                // PROPERTY browsing menu — user can inspect each property subsection.
                while (!back_to_main) {
                    std::cout << "\n--- SHOW MENU ---\n";
                    std::cout << "1. Metadata\n";
                    std::cout << "2. Properties\n";
                    std::cout << "3. Models\n";
                    std::cout << "0. Back (to main menu)\n";
                    int top_choice = ask_choice("Choose: ");
                    if (top_choice == 0) break;
                    if (top_choice == 1) { show_metadata(root); continue; }

                    if (top_choice == 2) {
                        if (!property) { std::cout << "No <Property> section found.\n"; continue; }
                        std::cout << "\n-- PROPERTY SUBSECTIONS --\n";
                        for (size_t i=0;i<property->children.size();++i) std::cout << "  " << (i+1) << ". " << property->children[i].name << "\n";
                        std::cout << "  0. Back\n";
                        int pch = ask_choice("Choose subsection: ");
                        if (pch == 0) continue;
                        if (pch < 1 || static_cast<size_t>(pch) > property->children.size()) { std::cout << "Invalid.\n"; continue; }
                        const XmlNode &picked = property->children[pch-1];
                        std::cout << "\n-- " << picked.name << " --\n";
                        show_node_children_as_fields(picked);
                        continue;
                    }

                    if (top_choice == 3) {
                        if (!model) { std::cout << "No <Model> section found.\n"; continue; }
                        std::cout << "\n-- MODELS --\n";
                        for (size_t i=0;i<model->children.size();++i) std::cout << "  " << (i+1) << ". " << model->children[i].name << "\n";
                        std::cout << "  0. Back\n";
                        int mch = ask_choice("Choose model: ");
                        if (mch == 0) continue;
                        if (mch < 1 || static_cast<size_t>(mch) > model->children.size()) { std::cout << "Invalid.\n"; continue; }
                        const XmlNode &pickedModel = model->children[mch-1];

                        // MODEL browsing menu — detect EOS model vs general model nodes.
                        if (pickedModel.name == "EOSModel") {
                            bool back_eos = false;
                            // EOS MODEL submenu — supports listing row indexes or picking by index.
                            while (!back_eos) {
                                std::cout << "\n-- EOS MODEL --\n";
                                std::cout << "1. List Row indexes\n";
                                std::cout << "2. Choose Row by index\n";
                                std::cout << "0. Back\n";
                                int eopt = ask_choice("Choose: ");
                                if (eopt == 0) { back_eos = true; break; }
                                if (eopt == 1) {
                                    auto rows = pickedModel.find_children("Row");
                                    if (rows.empty()) { std::cout << "No <Row> elements found.\n"; continue; }
                                    std::cout << "Rows found (indexes):\n";
                                    for (const XmlNode* r : rows) {
                                        auto idx = r->attr("index");
                                        std::cout << "  - " << (idx ? *idx : "(no index)") << "\n";
                                    }
                                    continue;
                                }
                                // For a specific EOS Row, allow browsing its child fields via submenu.
                                if (eopt == 2) {
                                    std::cout << "Enter row index (e.g. 5): ";
                                    std::string ridx = readline_trim();
                                    const XmlNode *row = find_eos_row_by_index(pickedModel, ridx);
                                    if (!row) { std::cout << "Row with index=" << ridx << " not found.\n"; continue; }
                                    bool back_row = false;
                                    while (!back_row) {
                                        std::cout << "\n-- Row index=" << ridx << " --\n";
                                        for (size_t i=0;i<row->children.size();++i) std::cout << "  " << (i+1) << ". " << row->children[i].name << "\n";
                                        std::cout << "  0. Back\n";
                                        int child_choice = ask_choice("Choose child: ");
                                        if (child_choice == 0) { back_row = true; break; }
                                        if (child_choice < 1 || static_cast<size_t>(child_choice) > row->children.size()) { std::cout << "Invalid.\n"; continue; }
                                        const XmlNode &child = row->children[child_choice-1];
                                        show_child_detail(child);
                                    }
                                    continue;
                                }
                                std::cout << "Invalid option.\n";
                            }
                            continue;
                        } else {
                            // General MODEL navigation — supports drilling into model subtrees.
                            bool back_model = false;
                            while (!back_model) {
                                std::cout << "\n-- MODEL: " << pickedModel.name << " --\n";
                                for (size_t i=0;i<pickedModel.children.size();++i) std::cout << "  " << (i+1) << ". " << pickedModel.children[i].name << "\n";
                                std::cout << "  0. Back\n";
                                int mc = ask_choice("Choose: ");
                                if (mc == 0) { back_model = true; break; }
                                if (mc < 1 || static_cast<size_t>(mc) > pickedModel.children.size()) { std::cout << "Invalid.\n"; continue; }
                                const XmlNode &selected = pickedModel.children[mc-1];
                                std::cout << "\n-- " << selected.name << " --\n";
                                show_node_children_as_fields(selected);
                                const XmlNode* childptr = choose_child_by_number(selected);
                                if (childptr) show_child_detail(*childptr);
                            }
                            continue;
                        }
                    }
                    std::cout << "Unknown option.\n";
                }
            }
        }
    } catch (const std::exception &e) {
        std::cerr << "Fatal: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
