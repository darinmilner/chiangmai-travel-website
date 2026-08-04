package models

// ContactRequest represents the contact form submission
type ContactRequest struct {
	Name    string `json:"name"`
	Email   string `json:"email"`
	Phone   string `json:"phone"`
	Subject string `json:"subject"`
	Message string `json:"message"`
	Website string `json:"website"` // Honeypot
}

// ContactResponse represents the contact form response
type ContactResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

// Button represents a call-to-action button
type Button struct {
	Text  string `json:"text"`
	URL   string `json:"url"`
	Icon  string `json:"icon"`
	Style string `json:"style"`
	Color string `json:"color"`
}

// Hero represents the hero section data
type Hero struct {
	Headline    string   `json:"headline"`
	Subheadline string   `json:"subheadline"`
	Buttons     []Button `json:"buttons"`
}

// Feature represents a business feature card
type Feature struct {
	Name        string `json:"name"`
	Image       string `json:"image"`
	Description string `json:"description"`
	Link        string `json:"link"`
	ColorClass  string `json:"color_class"`
	Location    string `json:"location"`
	Badge       string `json:"badge"`
}

// Reason represents a "Why Stay With Us" item
type Reason struct {
	Icon  string `json:"icon"`
	Title string `json:"title"`
	Text  string `json:"text"`
}

// Testimonial represents a guest review
type Testimonial struct {
	Name     string `json:"name"`
	Photo    string `json:"photo"`
	Text     string `json:"text"`
	Details  string `json:"details"`
	Location string `json:"location"`
	Rating   int    `json:"rating"`
}

// CTA represents the call-to-action section
type CTA struct {
	Title   string   `json:"title"`
	Text    string   `json:"text"`
	Buttons []Button `json:"buttons"`
}

// HomePageData is the complete homepage data structure
type HomePageData struct {
	Title        string        `json:"title"`
	Description  string        `json:"description"`
	ActivePage   string        `json:"active_page"`
	PageContent  string        `json:"page_content"` // Template name to render
	Hero         Hero          `json:"hero"`
	Features     []Feature     `json:"features"`
	Reasons      []Reason      `json:"reasons"`
	Testimonials []Testimonial `json:"testimonials"`
	CTA          CTA           `json:"cta"`
}

// ImageInfo holds information about an image including its paths
type ImageInfo struct {
	Full   string `json:"full"`
	Thumb  string `json:"thumb"`
	Medium string `json:"medium"`
	Alt    string `json:"alt"`
	Width  int    `json:"width"`
	Height int    `json:"height"`
}

// VillaPageData represents the data for the villa page
type VillaPageData struct {
	Title      string      `json:"title"`
	ActivePage string      `json:"activePage"`
	Images     []ImageInfo `json:"images"`
	ImagesJSON string      `json:"imagesJSON"`
}

// ImageServiceConfig holds configuration for image services
type ImageServiceConfig struct {
	// S3 configuration
	S3Bucket      string
	S3Region      string
	S3Prefix      string
	CloudFrontURL string

	// Local configuration
	LocalImageDir string
	UseLocal      bool

	// Cache settings
	CacheTTL    time.Duration
	EnableCache bool
}

// ImageCache holds cached image information
type ImageCache struct {
	Images    []ImageInfo
	UpdatedAt time.Time
	TTL       time.Duration
}

// IsExpired checks if the cache is expired
func (c *ImageCache) IsExpired() bool {
	if c.TTL == 0 {
		return false
	}
	return time.Since(c.UpdatedAt) > c.TTL
}
