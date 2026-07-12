package models

type HomePageData struct {
	Title        string        `json:"title"`
	Description  string        `json:"description"`
	ActivePage   string        `json:"active_page"`
	PageContent  string        `json:"page_content"`
	Hero         Hero          `json:"hero"`
	Features     []Feature     `json:"features"`
	Reasons      []Reason      `json:"reasons"`
	Testimonials []Testimonial `json:"testimonials"`
	CTA          CTA           `json:"cta"`
}

type Button struct {
	Text  string `json:"text"`
	URL   string `json:"url"`
	Icon  string `json:"icon"`
	Style string `json:"style"`
	Color string `json:"color"`
}

type Hero struct {
	Headline    string   `json:"headline"`
	Subheadline string   `json:"subheadline"`
	Buttons     []Button `json:"buttons"`
}

type Feature struct {
	Name        string `json:"name"`
	Image       string `json:"image"`
	Description string `json:"description"`
	Link        string `json:"link"`
	ColorClass  string `json:"color_class"`
	Location    string `json:"location"`
	Badge       string `json:"badge"`
}

type Reason struct {
	Icon  string `json:"icon"`
	Title string `json:"title"`
	Text  string `json:"text"`
}

type Testimonial struct {
	Name     string `json:"name"`
	Photo    string `json:"photo"`
	Text     string `json:"text"`
	Details  string `json:"details"`
	Location string `json:"location"`
	Rating   int    `json:"rating"`
}

type CTA struct {
	Title   string   `json:"title"`
	Text    string   `json:"text"`
	Buttons []Button `json:"buttons"`
}
