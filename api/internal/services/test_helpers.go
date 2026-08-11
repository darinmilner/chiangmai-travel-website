package services

import (
	"os"
	"path/filepath"
	"testing"

	"api/internal/models"
)

// TestConfig holds test configuration
type TestConfig struct {
	ProjectRoot string
	ImageDir    string
	TempDir     string
}

// SetupTestEnvironment creates a test environment
func SetupTestEnvironment(t *testing.T) *TestConfig {
	t.Helper()

	// Get project root
	projectRoot, err := os.Getwd()
	if err != nil {
		t.Skip("Could not determine project root, skipping test")
		return nil
	}

	// Navigate to project root (we're in internal/services)
	projectRoot = filepath.Dir(filepath.Dir(projectRoot))

	// Create temp directory for test images
	tempDir, err := os.MkdirTemp("", "villa-test-*")
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}

	// Create image directory structure
	imageDir := filepath.Join(tempDir, "static/images/villa")
	if err := os.MkdirAll(imageDir, 0755); err != nil {
		t.Fatalf("Failed to create image dir: %v", err)
	}

	t.Cleanup(func() {
		os.RemoveAll(tempDir)
	})

	return &TestConfig{
		ProjectRoot: projectRoot,
		ImageDir:    imageDir,
		TempDir:     tempDir,
	}
}

// CreateTestImage creates a test image file
func CreateTestImage(t *testing.T, dir, name string) string {
	t.Helper()

	path := filepath.Join(dir, name)
	// Create empty file (or with minimal content for testing)
	f, err := os.Create(path)
	if err != nil {
		t.Fatalf("Failed to create test image: %v", err)
	}
	defer f.Close()

	// Write minimal JPEG data (just for file existence testing)
	// In real tests, you'd use actual image data
	f.WriteString("fake image data")

	return path
}

// CreateTestImages creates multiple test images
func CreateTestImages(t *testing.T, dir string, names []string) []string {
	t.Helper()

	var paths []string
	for _, name := range names {
		path := CreateTestImage(t, dir, name)
		paths = append(paths, path)
	}
	return paths
}

// MockImageInfo creates mock image info for testing
func MockImageInfo(filename string) models.ImageInfo {
	return models.ImageInfo{
		Full:   "/static/images/villa/" + filename,
		Thumb:  "/static/images/villa/thumb_" + filename,
		Medium: "/static/images/villa/medium_" + filename,
		Alt:    filename,
		Width:  1200,
		Height: 800,
	}
}

// MockImageInfoList creates a list of mock image info
func MockImageInfoList(filenames []string) []models.ImageInfo {
	var images []models.ImageInfo
	for _, name := range filenames {
		images = append(images, MockImageInfo(name))
	}
	return images
}

// AssertImageInfoEquals compares two ImageInfo structs
func AssertImageInfoEquals(t *testing.T, expected, actual models.ImageInfo) {
	t.Helper()

	if expected.Full != actual.Full {
		t.Errorf("Full URL mismatch: expected %s, got %s", expected.Full, actual.Full)
	}
	if expected.Thumb != actual.Thumb {
		t.Errorf("Thumb URL mismatch: expected %s, got %s", expected.Thumb, actual.Thumb)
	}
	if expected.Medium != actual.Medium {
		t.Errorf("Medium URL mismatch: expected %s, got %s", expected.Medium, actual.Medium)
	}
	if expected.Alt != actual.Alt {
		t.Errorf("Alt text mismatch: expected %s, got %s", expected.Alt, actual.Alt)
	}
}
