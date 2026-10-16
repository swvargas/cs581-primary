{
  description = "CS 581 Python lab development environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { nixpkgs, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
    in
    {
      devShells = nixpkgs.lib.genAttrs systems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.bashInteractive
              pkgs.openssl
              (pkgs.python312.withPackages (python: [
                python.flask
                python.gunicorn
                # Avoid the upstream test-only Twisted/AnyIO dependency chain.
                (python.pymodbus.overridePythonAttrs (_: { doCheck = false; }))
                python.requests
              ]))
            ];
          };
        });
    };
}
