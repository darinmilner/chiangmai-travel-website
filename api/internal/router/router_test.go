package router

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestTemplateFilesExist(t *testing.T) {
	// Get the project root (where go.mod is)
	projectRoot := filepath.Join("..", "..")
	t.Logf("📂 Project root: %s", projectRoot)

	// Test that template files exist on disk
	requiredFiles := []string{
		filepath.Join(projectRoot, "templates", "layouts", "base.html"),
		filepath.Join(projectRoot, "templates", "partials", "header.html"),
		filepath.Join(projectRoot, "templates", "partials", "footer.html"),
		filepath.Join(projectRoot, "templates", "pages", "index.html"),
	}

	for _, file := range requiredFiles {
		t.Run(file, func(t *testing.T) {
			_, err := os.Stat(file)
			if err != nil {
				t.Errorf("❌ File not found: %s", file)
			} else {
				t.Logf("✅ File exists: %s", file)
			}
		})
	}
}

func TestTemplateFilesContent(t *testing.T) {
	projectRoot := filepath.Join("..", "..")

	tests := []struct {
		file     string
		expected string
	}{
		{filepath.Join(projectRoot, "templates", "layouts", "base.html"), `{{ define "base" }}`},
		{filepath.Join(projectRoot, "templates", "partials", "header.html"), `{{ define "header" }}`},
		{filepath.Join(projectRoot, "templates", "partials", "footer.html"), `{{ define "footer" }}`},
		{filepath.Join(projectRoot, "templates", "pages", "index.html"), `{{ define "content" }}`},
	}

	for _, tt := range tests {
		t.Run(tt.file, func(t *testing.T) {
			content, err := os.ReadFile(tt.file)
			if err != nil {
				t.Errorf("❌ Could not read file: %v", err)
				return
			}
			if !strings.Contains(string(content), tt.expected) {
				t.Errorf("❌ File %s does not contain %q", tt.file, tt.expected)
			} else {
				t.Logf("✅ File %s contains %q", tt.file, tt.expected)
			}
		})
	}
}

func TestRouterSetup(t *testing.T) {
	t.Run("SetupRouter should not panic", func(t *testing.T) {
		defer func() {
			if r := recover(); r != nil {
				t.Logf("❌ SetupRouter panicked: %v", r)
				t.Fail()
			}
		}()

		router := SetupRouter()
		if router == nil {
			t.Error("❌ SetupRouter returned nil")
		} else {
			t.Log("✅ SetupRouter created successfully")
		}
	})
}