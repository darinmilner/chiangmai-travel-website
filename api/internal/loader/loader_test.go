package loader

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"api/internal/models"
)

func TestLoadHomePageData(t *testing.T) {
	// Get the current working directory
	cwd, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get working directory: %v", err)
	}
	t.Logf("📂 Current working directory: %s", cwd)

	// Check if data directory exists
	dataDir := filepath.Join(cwd, "data")
	if _, err := os.Stat(dataDir); os.IsNotExist(err) {
		// Try one level up (if running from api/internal/loader)
		dataDir = filepath.Join(cwd, "..", "..", "data")
		if _, err := os.Stat(dataDir); os.IsNotExist(err) {
			t.Fatalf("❌ Data directory not found. Looked in: %s and %s",
				filepath.Join(cwd, "data"),
				filepath.Join(cwd, "..", "..", "data"))
		}
	}
	t.Logf("📂 Data directory found at: %s", dataDir)

	// List files in data directory
	files, err := os.ReadDir(dataDir)
	if err != nil {
		t.Fatalf("❌ Could not read data directory: %v", err)
	}
	t.Logf("📂 Files in data directory:")
	for _, f := range files {
		t.Logf("  - %s", f.Name())
	}

	// Test loading the data
	data, err := LoadHomePageData()
	if err != nil {
		t.Fatalf("❌ LoadHomePageData() failed: %v", err)
	}

	// Verify features
	if len(data.Features) == 0 {
		t.Errorf("❌ Expected at least 1 feature, got %d", len(data.Features))
	} else {
		t.Logf("✅ Features: %d", len(data.Features))
		// Log first feature
		if len(data.Features) > 0 {
			t.Logf("   First feature: %+v", data.Features[0])
		}
	}

	// Verify reasons
	if len(data.Reasons) == 0 {
		t.Errorf("❌ Expected at least 1 reason, got %d", len(data.Reasons))
	} else {
		t.Logf("✅ Reasons: %d", len(data.Reasons))
	}

	// Verify testimonials
	if len(data.Testimonials) == 0 {
		t.Errorf("❌ Expected at least 1 testimonial, got %d", len(data.Testimonials))
	} else {
		t.Logf("✅ Testimonials: %d", len(data.Testimonials))
	}

	// Verify JSON files are valid
	t.Run("ValidateJSONFiles", func(t *testing.T) {
		jsonFiles := []string{"features.json", "reasons.json", "testimonials.json"}
		for _, fileName := range jsonFiles {
			filePath := filepath.Join(dataDir, fileName)
			t.Run(fileName, func(t *testing.T) {
				file, err := os.Open(filePath)
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
	})
}

// TestLoadFeatures tests loading just the features file
func TestLoadFeatures(t *testing.T) {
	// Get the current working directory
	cwd, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get working directory: %v", err)
	}

	// Try to find data directory
	dataDir := filepath.Join(cwd, "data")
	if _, err := os.Stat(dataDir); os.IsNotExist(err) {
		dataDir = filepath.Join(cwd, "..", "..", "data")
		if _, err := os.Stat(dataDir); os.IsNotExist(err) {
			t.Skip("Skipping test: data directory not found")
		}
	}

	filePath := filepath.Join(dataDir, "features.json")
	file, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("Could not open features.json: %v", err)
	}
	defer file.Close()

	var result struct {
		Features []models.Feature `json:"features"`
	}
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&result); err != nil {
		t.Fatalf("Failed to decode features.json: %v", err)
	}

	t.Logf("✅ Loaded %d features directly", len(result.Features))
	if len(result.Features) == 0 {
		t.Error("❌ No features found in features.json")
	}
}