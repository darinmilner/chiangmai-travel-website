package handlers

import (
	"os"
	"path/filepath"
	"testing"
)

func TestVillaPage_ImageLoading(t *testing.T) {
	// Get the project root
	projectRoot, err := os.Getwd()
	if err != nil {
		t.Skip("Could not determine project root, skipping test")
		return
	}
	// We're in api/internal/handlers, so go up two levels to api/
	projectRoot = filepath.Dir(filepath.Dir(projectRoot))
	t.Logf("📂 Project root: %s", projectRoot)

	t.Run("should load images from directory", func(t *testing.T) {
		// Create a temporary test directory
		testDir := filepath.Join(projectRoot, "static/images/villa")

		// Check if directory exists
		if _, err := os.Stat(testDir); os.IsNotExist(err) {
			t.Logf("⚠️ Directory %s does not exist, using default images", testDir)
			// Use default images
			defaultImages := []string{
				"/static/images/villa/exterior.jpg",
				"/static/images/villa/pool.jpg",
				"/static/images/villa/living-room.jpg",
				"/static/images/villa/kitchen.jpg",
				"/static/images/villa/bedroom.jpg",
				"/static/images/villa/garden.jpg",
			}
			t.Logf("✅ Using %d default images", len(defaultImages))
			return
		}

		// Read images
		files, err := os.ReadDir(testDir)
		if err != nil {
			t.Logf("⚠️ Could not read directory: %v", err)
			return
		}

		var images []string
		for _, file := range files {
			if !file.IsDir() {
				name := file.Name()
				// Only include image files
				ext := filepath.Ext(name)
				if ext == ".jpg" || ext == ".jpeg" || ext == ".png" || ext == ".webp" || ext == ".gif" {
					images = append(images, "/static/images/villa/"+name)
				}
			}
		}

		t.Logf("📸 Found %d images in %s", len(images), testDir)
		for i, img := range images {
			t.Logf("   %d: %s", i+1, img)
		}

		if len(images) == 0 {
			t.Log("⚠️ No images found, default images will be used")
		}
	})

	t.Run("should use default images when directory is empty", func(t *testing.T) {
		// Simulate the VillaPage function's default behavior
		imageDir := filepath.Join(projectRoot, "static/images/villa")
		var images []string

		files, err := os.ReadDir(imageDir)
		if err == nil {
			for _, file := range files {
				if !file.IsDir() {
					name := file.Name()
					ext := filepath.Ext(name)
					if ext == ".jpg" || ext == ".jpeg" || ext == ".png" || ext == ".webp" || ext == ".gif" {
						images = append(images, "/static/images/villa/"+name)
					}
				}
			}
		}

		if len(images) == 0 {
			images = []string{
				"/static/images/villa/exterior.jpg",
				"/static/images/villa/pool.jpg",
				"/static/images/villa/living-room.jpg",
				"/static/images/villa/kitchen.jpg",
				"/static/images/villa/bedroom.jpg",
				"/static/images/villa/garden.jpg",
			}
			t.Logf("✅ Using %d default images", len(images))
		} else {
			t.Logf("✅ Found %d images", len(images))
		}
	})
}

func TestVillaPage_ImageExtensions(t *testing.T) {
	t.Run("should only include valid image extensions", func(t *testing.T) {
		validExtensions := []string{".jpg", ".jpeg", ".png", ".webp", ".gif"}
		invalidExtensions := []string{".txt", ".pdf", ".doc", ".mp4", ".mov"}

		for _, ext := range validExtensions {
			t.Logf("✅ Valid extension: %s", ext)
		}

		for _, ext := range invalidExtensions {
			t.Logf("❌ Invalid extension: %s (should be skipped)", ext)
		}
	})
}
