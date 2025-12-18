#include <iostream>
#include <string>
#include <cstdio>
#include <cstdint>   // <-- REQUIRED for uint32_t

// --- FNV-1a 32-bit hash ---
uint32_t fnv1a(const std::string &s) {
    uint32_t hash = 0x811C9DC5; // offset basis
    for (unsigned char c : s) {
        hash ^= c;
        hash *= 16777619u;      // FNV prime
    }
    return hash;
}

// Convert to 8-digit uppercase hex
std::string to_hex8(uint32_t value) {
    char buf[16];
    std::sprintf(buf, "%08X", value);
    return std::string(buf);
}

int main() {
    std::string name;
    std::string version;

    std::cout << "Enter material name (exactly as in <Id> tag): ";
    std::getline(std::cin, name);

    std::cout << "Enter xml version: ";
    std::getline(std::cin, version);

    if (name.empty()) {
        std::cout << "ERROR: Name cannot be empty.\n";
        return 1;
    }

    uint32_t h = fnv1a(name);
    std::string checksum = to_hex8(h);

    std::cout << "\n========== RESULT ==========\n";
    std::cout << "Material Name : " << name << "\n";
    std::cout << "Checksum       : " << checksum << "\n";
    std::cout << "\nPaste this inside your XML:\n";
    std::cout << "    <Version meaning=\"schema_version\">" << version << "-" << checksum << "</Version>\n";
    std::cout << "============================\n";

    return 0;
}
