package services

import (
	"context"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"api/internal/models"
)

// LocalImageService handles fetching images from local filesystem
type LocalImageService struct {
	*BaseImageService
}

// NewLocalImageService creates a new local image service
func NewLocalImageService(config models.ImageServiceConfig) *LocalImageService {
	if config.LocalImageDir != "" {
		os.MkdirAll(config.LocalImageDir, 0755)
	}

	return &LocalImageService{
		BaseImageService: NewBaseImageService(config),
	}
}

// GetImages retrieves images from local filesystem
func (s *LocalImageService) GetImages(ctx context.Context) ([]models.ImageInfo, error) {
	if s.Config.EnableCache && len(s.Cache.Images) > 0 && !s.Cache.IsExpired() {
		log.Printf("Returning %d images from local cache", len(s.Cache.Images))
		return s.Cache.Images, nil
	}

	log.Printf("Fetching images from local directory: %s", s.Config.LocalImageDir)

	files, err := os.ReadDir(s.Config.LocalImageDir)
	if err != nil {
		return nil, fmt.Errorf("failed to read image directory: %v", err)
	}

	var images []models.ImageInfo

	for _, file := range files {
		if file.IsDir() {
			continue
		}

		name := file.Name()
		ext := strings.ToLower(filepath.Ext(name))

		if !isLocalImageExt(ext) {
			continue
		}

		// Skip processed files
		if strings.Contains(name, "thumb_") || strings.Contains(name, "medium_") ||
			strings.Contains(name, "carousel_") {
			continue
		}

		info := s.getLocalImageInfo(name)
		if info != nil {
			images = append(images, *info)
		}
	}

	if s.Config.EnableCache {
		s.Cache.Images = images
		s.Cache.UpdatedAt = time.Now()
	}

	log.Printf("Retrieved %d images from local directory", len(images))
	return images, nil
}

// GetImagesJSON returns images as JSON string
func (s *LocalImageService) GetImagesJSON(ctx context.Context) (string, error) {
	images, err := s.GetImages(ctx)
	if err != nil {
		return "", err
	}

	// Convert to JSON manually
	result := "["
	for i, img := range images {
		if i > 0 {
			result += ","
		}
		result += fmt.Sprintf(`{"full":"%s","thumb":"%s","medium":"%s","alt":"%s","width":%d,"height":%d}`,
			img.Full, img.Thumb, img.Medium, img.Alt, img.Width, img.Height)
	}
	result += "]"

	return result, nil
}

// GetVillaPageData returns data for the villa page
func (s *LocalImageService) GetVillaPageData(ctx context.Context, title, activePage string) (*models.VillaPageData, error) {
	images, err := s.GetImages(ctx)
	if err != nil {
		return nil, err
	}

	imagesJSON, err := s.GetImagesJSON(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal images: %v", err)
	}

	return &models.VillaPageData{
		Title:      title,
		ActivePage: activePage,
		Images:     images,
		ImagesJSON: imagesJSON,
	}, nil
}

// getLocalImageInfo creates ImageInfo from local file
func (s *LocalImageService) getLocalImageInfo(filename string) *models.ImageInfo {
	baseName := strings.TrimSuffix(filename, filepath.Ext(filename))

	// Build local paths
	fullPath := filepath.Join(s.Config.LocalImageDir, filename)
	thumbPath := filepath.Join(s.Config.LocalImageDir, fmt.Sprintf("thumb_%s.jpg", baseName))
	mediumPath := filepath.Join(s.Config.LocalImageDir, fmt.Sprintf("medium_%s.jpg", baseName))

	// Check if processed versions exist
	thumbExists := fileExists(thumbPath)
	mediumExists := fileExists(mediumPath)

	// If using local, serve files directly
	fullURL := "/" + fullPath
	thumbURL := "/" + thumbPath
	mediumURL := "/" + mediumPath

	// If processed versions don't exist, use original
	if !thumbExists {
		thumbURL = fullURL
	}
	if !mediumExists {
		mediumURL = fullURL
	}

	return &models.ImageInfo{
		Full:   fullURL,
		Thumb:  thumbURL,
		Medium: mediumURL,
		Alt:    strings.ReplaceAll(baseName, "-", " "),
		Width:  1200,
		Height: 800,
	}
}

func isLocalImageExt(ext string) bool {
	validExts := []string{".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
	for _, validExt := range validExts {
		if ext == validExt {
			return true
		}
	}
	return false
}

func fileExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}
