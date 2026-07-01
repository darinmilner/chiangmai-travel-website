package handlers

import (
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
)

func HealthCheck(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{
        "status":    "ok",
        "service":   "chiang-mai-business",
        "timestamp": time.Now().UTC().Format(time.RFC3339),
    })
}

func HomePage(c *gin.Context) {
    data := gin.H{
        "Title":       "Chiang Mai Villa & Hostel",
        "Description": "Your halal-friendly home in Chiang Mai. Villa, hostel, and halal meat shop.",
        "ActivePage":  "home",
        "Testimonial": gin.H{
            "Name":     "Your Name",
            "Photo":    "/static/images/testimonial-photo.jpg",
            "Text":     "I visited this shop several times during my stay in Chiang Mai. The variety is impressive, from local sausages to fresh beef and chicken, and even samosas and sticky rice. The owners are incredibly welcoming, and their English is excellent. It's a must-visit for anyone looking for high-quality halal products in Chiang Mai.",
            "Details":  "Digital Nomad & Food Enthusiast",
            "Location": "Chiang Mai, Thailand",
        },
        "Features": []gin.H{
            {
                "Name":        "The Villa",
                "Image":       "/static/images/villa.jpg",
                "Description": "Private villa with pool, garden, and full kitchen. Perfect for families and groups.",
                "Link":        "/villa",
                "ColorClass":  "green",
            },
            {
                "Name":        "The Hostel",
                "Image":       "/static/images/hostel.jpg",
                "Description": "Comfortable dorms and private rooms. Fast WiFi, common areas, and a welcoming vibe.",
                "Link":        "/hostel",
                "ColorClass":  "olive",
            },
            {
                "Name":        "The Meat Shop",
                "Image":       "/static/images/meatshop.jpg",
                "Description": "Fresh, high-quality halal meat. Trusted by locals and travelers alike.",
                "Link":        "/meatshop",
                "ColorClass":  "brown",
            },
        },
        "Reasons": []gin.H{
            {
                "Icon":  "fa-mosque",
                "Title": "Steps from the Mosque",
                "Text":  "Just 3 minutes walking distance to the local mosque.",
            },
            {
                "Icon":  "fa-utensils",
                "Title": "Halal Food Nearby",
                "Text":  "Halal restaurants and our own meat shop nearby.",
            },
            {
                "Icon":  "fa-wifi",
                "Title": "Digital Nomad Ready",
                "Text":  "Fast WiFi, workspaces, and a productive environment.",
            },
        },
    }

    c.HTML(http.StatusOK, "index.html", data)
}