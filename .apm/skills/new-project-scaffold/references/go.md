# Go Reference

## Toolchain

| Concern | Tool |
|---|---|
| Version | Go 1.22+ |
| Module system | Go modules |
| Linter | golangci-lint |
| Formatter | gofmt / goimports (built-in) |
| Test runner | `go test` (built-in) |
| Coverage | `go test -cover` (built-in) |

---

## `go.mod` template

```
module github.com/<org>/<project>

go 1.22
```

## Project layout

```
<project>/
├── cmd/
│   └── <project>/
│       └── main.go
├── internal/
│   └── core/
│       ├── core.go
│       └── core_test.go
├── .github/
│   └── workflows/
│       └── ci.yml
├── .golangci.yml
├── go.mod
├── go.sum
└── README.md
```

## `.golangci.yml`

```yaml
linters:
  enable:
    - gofmt
    - goimports
    - govet
    - errcheck
    - staticcheck
    - unused
    - gosimple
    - revive

linters-settings:
  goimports:
    local-prefixes: github.com/<org>/<project>

issues:
  max-issues-per-linter: 0
  max-same-issues: 0
```

## Test file pattern

```go
// internal/core/core_test.go
package core_test

import (
    "testing"

    "github.com/<org>/<project>/internal/core"
)

func TestMyFunction(t *testing.T) {
    t.Run("valid input", func(t *testing.T) {
        result, err := core.MyFunction("hello")
        if err != nil {
            t.Fatalf("unexpected error: %v", err)
        }
        if result != "HELLO" {
            t.Errorf("got %q, want %q", result, "HELLO")
        }
    })

    t.Run("empty input returns empty", func(t *testing.T) {
        result, err := core.MyFunction("")
        if err != nil {
            t.Fatalf("unexpected error: %v", err)
        }
        if result != "" {
            t.Errorf("got %q, want empty", result)
        }
    })

    t.Run("invalid input returns error", func(t *testing.T) {
        _, err := core.MyFunction("   ")
        if err == nil {
            t.Fatal("expected error, got nil")
        }
    })
}
```

## GitHub Actions — CI

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
          cache: true

      - name: Lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: latest

      - name: Test
        run: go test -v -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Coverage check
        run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | tr -d '%')
          echo "Coverage: $COVERAGE%"
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage below 80%"
            exit 1
          fi

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.out
```

## `.gitignore`

```
# Binaries
*.exe
*.exe~
*.dll
*.so
*.dylib
/<project-name>

# Test binary
*.test

# Coverage
*.out
coverage.out

# Go workspace
go.work
go.work.sum

.env
```
