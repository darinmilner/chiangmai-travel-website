package router

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
)

func TestSetupRouter(t *testing.T) {
	originalDir, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}

	projectRoot := filepath.Join("..", "..")
	if err := os.Chdir(projectRoot); err != nil {
		t.Skip("Cannot locate project root")
	}

	defer os.Chdir(originalDir)

	router := SetupRouter()

	tests := []struct {
		name string
		url  string
	}{
		{"home", "/"},
		{"villa", "/villa"},
		{"hostel", "/hostel"},
		{"meatshop", "/meatshop"},
		{"blog", "/blog"},
		{"contact", "/contact"},
		{"health", "/health"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, tt.url, nil)
			w := httptest.NewRecorder()

			router.ServeHTTP(w, req)

			if w.Code != http.StatusOK {
				t.Fatalf("%s returned %d\nBody:\n%s",
					tt.url,
					w.Code,
					w.Body.String())
			}
		})
	}
}
