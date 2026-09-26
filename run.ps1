# PowerShell runner for tool-ghcr-docker-packager
param(
    [string]$Command = "health",
    [string]$Target = ".",
    [string]$Owner = "octocat"
)

switch ($Command) {
    "setup"    { python main.py setup }
    "run"      { python main.py run --target $Target }
    "test"     { python main.py test }
    "health"   { python main.py health }
    "clean"    { python main.py clean }
    "build"    { python main.py build --target $Target --owner $Owner }
    "workflow" { python main.py workflow --target $Target --owner $Owner }
    Default    { python main.py $Command }
}
