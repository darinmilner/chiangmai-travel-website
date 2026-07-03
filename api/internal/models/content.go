package models

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
	Hero         Hero          `json:"hero"`
	Features     []Feature     `json:"features"`
	Reasons      []Reason      `json:"reasons"`
	Testimonials []Testimonial `json:"testimonials"`
	CTA          CTA           `json:"cta"`
}
