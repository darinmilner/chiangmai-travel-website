package loader

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestLoadHomePageData(t *testing.T) {
	t.Log("🔍 Testing LoadHomePageData...")

	// Get current working directory
	cwd, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get working directory: %v", err)
	}
	t.Logf("📂 Current working directory: %s", cwd)

	// Find data directory
	dataDir := filepath.Join(cwd, "..", "..", "data")
	if _, err := os.Stat(dataDir); os.IsNotExist(err) {
		dataDir = filepath.Join(cwd, "data")
		if _, err := os.Stat(dataDir); os.IsNotExist(err) {
			t.Skip("Skipping test: data directory not found")
		}
	}
	t.Logf("📂 Data directory: %s", dataDir)

	// Verify JSON files exist
	jsonFiles := []string{"features.json", "reasons.json", "testimonials.json"}
	for _, f := range jsonFiles {
		path := filepath.Join(dataDir, f)
		if _, err := os.Stat(path); os.IsNotExist(err) {
			t.Errorf("❌ File not found: %s", path)
		} else {
			t.Logf("✅ File exists: %s", path)
		}
	}

	// Test loading data
	data, err := LoadHomePageData()
	if err != nil {
		t.Fatalf("❌ LoadHomePageData failed: %v", err)
	}

	t.Log("✅ LoadHomePageData succeeded")

	// Check features
	t.Run("Features should be loaded", func(t *testing.T) {
		if len(data.Features) == 0 {
			t.Errorf("❌ Expected features, got %d", len(data.Features))
		} else {
			t.Logf("✅ Loaded %d features", len(data.Features))
			for i, f := range data.Features {
				t.Logf("   Feature %d: %s", i+1, f.Name)
			}
		}
	})

	// Check reasons
	t.Run("Reasons should be loaded", func(t *testing.T) {
		if len(data.Reasons) == 0 {
			t.Errorf("❌ Expected reasons, got %d", len(data.Reasons))
		} else {
			t.Logf("✅ Loaded %d reasons", len(data.Reasons))
			for i, r := range data.Reasons {
				t.Logf("   Reason %d: %s", i+1, r.Title)
			}
		}
	})

	// Check testimonials
	t.Run("Testimonials should be loaded", func(t *testing.T) {
		if len(data.Testimonials) == 0 {
			t.Errorf("❌ Expected testimonials, got %d", len(data.Testimonials))
		} else {
			t.Logf("✅ Loaded %d testimonials", len(data.Testimonials))
			for i, tm := range data.Testimonials {
				t.Logf("   Testimonial %d: %s", i+1, tm.Name)
			}
		}
	})

	// Check Hero
	t.Run("Hero Headline should be set", func(t *testing.T) {
		if data.Hero.Headline == "" {
			t.Errorf("❌ Hero Headline is empty")
		} else {
			t.Logf("✅ Hero Headline: '%s'", data.Hero.Headline)
		}
	})

	// Check CTA
	t.Run("CTA Title should be set", func(t *testing.T) {
		if data.CTA.Title == "" {
			t.Errorf("❌ CTA Title is empty")
		} else {
			t.Logf("✅ CTA Title: '%s'", data.CTA.Title)
		}
	})

	// Debug: Print full data structure
	t.Log("📊 Full data summary:")
	t.Logf("   Title: %s", data.Title)
	t.Logf("   Description: %s", data.Description)
	t.Logf("   ActivePage: %s", data.ActivePage)
	t.Logf("   Hero Headline: %s", data.Hero.Headline)
	t.Logf("   Hero Subheadline: %s", data.Hero.Subheadline)
	t.Logf("   CTA Title: %s", data.CTA.Title)
	t.Logf("   CTA Text: %s", data.CTA.Text)
}

// TestJSONFilesValid verifies the JSON files are properly formatted
func TestJSONFilesValid(t *testing.T) {
	cwd, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get working directory: %v", err)
	}

	dataDir := filepath.Join(cwd, "..", "..", "data")
	if _, err := os.Stat(dataDir); os.IsNotExist(err) {
		dataDir = filepath.Join(cwd, "data")
		if _, err := os.Stat(dataDir); os.IsNotExist(err) {
			t.Skip("Skipping test: data directory not found")
		}
	}

	jsonFiles := []string{"features.json", "reasons.json", "testimonials.json"}
	for _, fileName := range jsonFiles {
		t.Run(fileName, func(t *testing.T) {
			path := filepath.Join(dataDir, fileName)
			file, err := os.Open(path)
			if err != nil {
				t.Fatalf("Could not open %s: %v", fileName, err)
			}
			defer file.Close()

			var raw interface{}
			decoder := json.NewDecoder(file)
			if err := decoder.Decode(&raw); err != nil {
				t.Errorf("❌ Invalid JSON in %s: %v", fileName, err)
			} else {
				t.Logf("✅ %s is valid JSON", fileName)
			}
		})
	}
}
