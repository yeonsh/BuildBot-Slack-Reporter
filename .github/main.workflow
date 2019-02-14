workflow "New workflow" {
  on = "push"
  resolves = ["Pyflakes Syntax Checker"]
}

action "Pyflakes Syntax Checker" {
  uses = "lgeiger/pyflakes-action@v1.0.1"
}
