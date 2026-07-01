package handlers

import (
    "net/http"

    "github.com/gin-gonic/gin"
)

// VillaPage handles the villa page
func VillaPage(c *gin.Context) {
    c.HTML(http.StatusOK, "villa", gin.H{
        "Title":      "The Villa",
        "ActivePage": "villa",
    })
}

// HostelPage handles the hostel page
func HostelPage(c *gin.Context) {
    c.HTML(http.StatusOK, "hostel", gin.H{
        "Title":      "The Hostel",
        "ActivePage": "hostel",
    })
}

// MeatShopPage handles the meat shop page
func MeatShopPage(c *gin.Context) {
    c.HTML(http.StatusOK, "meatshop", gin.H{
        "Title":      "The Meat Shop",
        "ActivePage": "meatshop",
    })
}

// BlogPage handles the blog page
func BlogPage(c *gin.Context) {
    c.HTML(http.StatusOK, "blog/list", gin.H{
        "Title":      "Blog",
        "ActivePage": "blog",
    })
}

// ContactPage handles the contact page
func ContactPage(c *gin.Context) {
    c.HTML(http.StatusOK, "contact", gin.H{
        "Title":      "Contact Us",
        "ActivePage": "contact",
    })
}