package loader

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"api/internal/models"
)

// LoadHomePageData loads all homepage data from JSON files
func LoadHomePageData() (*models.HomePageData, error) {
	log.Println("🔴 LOADER: LoadHomePageData() called")

	// Get current working directory
	cwd, err := os.Getwd()
	if err != nil {
		return nil, fmt.Errorf("failed to get working directory: %w", err)
	}
	log.Printf("📂 Current working directory: %s", cwd)

	// Try to find data directory
	dataDir := filepath.Join(cwd, "data")
	if _, err := os.Stat(dataDir); os.IsNotExist(err) {
		dataDir = filepath.Join(cwd, "..", "data")
		if _, err := os.Stat(dataDir); os.IsNotExist(err) {
			dataDir = filepath.Join(cwd, "..", "..", "data")
			if _, err := os.Stat(dataDir); os.IsNotExist(err) {
				return nil, fmt.Errorf("could not find data directory in any of: ./data, ../data, ../../data")
			}
		}
	}

	log.Printf("✅ Found data directory at: %s", dataDir)

	// List files in data directory
	files, err := os.ReadDir(dataDir)
	if err != nil {
		return nil, fmt.Errorf("could not read data directory %s: %w", dataDir, err)
	}
	log.Printf("📂 Files in data directory:")
	for _, f := range files {
		log.Printf("  - %s", f.Name())
	}

	// Initialize with default data
	data := &models.HomePageData{
		Title:       "Chiang Mai Villa & Hostel",
		Description: "Your halal-friendly home in Chiang Mai",
		ActivePage:  "home",
		Hero: models.Hero{
			Headline:    `Your <span class="text-amber">Chiang Mai</span> Escape`,
			Subheadline: "Choose between our peaceful resort-style villa (11km from the mosque) or our convenient city hostel, steps from the mosque.",
			Buttons: []models.Button{
				{Text: "Book the Villa", URL: "/villa", Icon: "fa-home", Style: "primary", Color: "amber"},
				{Text: "Book the Hostel", URL: "/hostel", Icon: "fa-bed", Style: "outline", Color: "white"},
			},
		},
		CTA: models.CTA{
			Title: "Ready to Book Your Stay?",
			Text:  "Contact us today and start your Chiang Mai adventure.",
			Buttons: []models.Button{
				{Text: "Contact Us", URL: "/contact", Icon: "fa-paper-plane", Style: "primary", Color: "amber"},
				{Text: "Chat on LINE", URL: "https://line.me/ti/p/[LINE_ID]", Icon: "fa-comment-dots", Style: "outline", Color: "white"},
			},
		},
	}

	// Load features with wrapper
	featuresPath := filepath.Join(dataDir, "features.json")
	log.Printf("📂 Loading features from: %s", featuresPath)
	var featuresWrapper struct {
		Features []models.Feature `json:"features"`
	}
	if err := loadJSONFile(featuresPath, &featuresWrapper); err != nil {
		return nil, fmt.Errorf("failed to load features.json: %w", err)
	}
	data.Features = featuresWrapper.Features
	log.Printf("✅ Loaded %d features", len(data.Features))

	// Load reasons with wrapper
	reasonsPath := filepath.Join(dataDir, "reasons.json")
	log.Printf("📂 Loading reasons from: %s", reasonsPath)
	var reasonsWrapper struct {
		Reasons []models.Reason `json:"reasons"`
	}
	if err := loadJSONFile(reasonsPath, &reasonsWrapper); err != nil {
		return nil, fmt.Errorf("failed to load reasons.json: %w", err)
	}
	data.Reasons = reasonsWrapper.Reasons
	log.Printf("✅ Loaded %d reasons", len(data.Reasons))

	// Load testimonials with wrapper
	testimonialsPath := filepath.Join(dataDir, "testimonials.json")
	log.Printf("📂 Loading testimonials from: %s", testimonialsPath)
	var testimonialsWrapper struct {
		Testimonials []models.Testimonial `json:"testimonials"`
	}
	if err := loadJSONFile(testimonialsPath, &testimonialsWrapper); err != nil {
		return nil, fmt.Errorf("failed to load testimonials.json: %w", err)
	}
	data.Testimonials = testimonialsWrapper.Testimonials
	log.Printf("✅ Loaded %d testimonials", len(data.Testimonials))

	log.Printf("🎉 LOADER: Successfully loaded all data")

	// Debug: verify hero headline is set
	log.Printf("🔍 Hero Headline: '%s'", data.Hero.Headline)

	return data, nil
}

// loadJSONFile loads a JSON file into the provided interface
func loadJSONFile(path string, v interface{}) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	return decoder.Decode(v)
}
