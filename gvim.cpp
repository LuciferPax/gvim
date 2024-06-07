#include <iostream>
#include <string>
#include <filesystem>

namespace fs = std::filesystem;

int main(int argc, char* argv[]) {
  fs::path exePath = fs::canonical(fs::path(argv[0])).remove_filename();

  exePath /= "gvim.py";

  std::string command = "python " + exePath.string();

  system(command.c_str());

  return 0;
}
