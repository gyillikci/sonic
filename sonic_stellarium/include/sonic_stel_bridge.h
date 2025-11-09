/**
 * SONIC-Stellarium Bridge
 *
 * Provides direct framebuffer access to Stellarium rendering without file I/O
 *
 * Key Features:
 * - Offscreen rendering (no GUI required)
 * - Direct memory access to rendered frames
 * - Real-time performance (60 FPS capable)
 * - Integration with SONIC crater detection
 *
 * Author: SONIC Navigation Team
 * License: GPL v2 (same as Stellarium)
 */

#pragma once

#include <QString>
#include <QImage>
#include <memory>

// Forward declarations to avoid heavy Qt includes
class QOffscreenSurface;
class QOpenGLFramebufferObject;
class QOpenGLContext;

namespace sonic {

/**
 * Main bridge class between SONIC and Stellarium
 *
 * This class manages an embedded Stellarium instance that renders
 * offscreen to a framebuffer, allowing direct pixel access without
 * file I/O or screen display.
 */
class StellariumBridge {
public:
    /**
     * Constructor
     *
     * @param width  Framebuffer width in pixels
     * @param height Framebuffer height in pixels
     */
    StellariumBridge(int width = 2048, int height = 2048);

    /**
     * Destructor
     */
    ~StellariumBridge();

    /**
     * Initialize Stellarium core without GUI
     *
     * @param configDir Optional path to Stellarium config directory
     * @return true if initialization succeeded
     */
    bool initialize(const QString& configDir = "");

    /**
     * Check if Stellarium is initialized and ready
     */
    bool isReady() const { return initialized_; }

    // ========== View Control ==========

    /**
     * Set field of view in degrees
     *
     * @param degrees FOV in degrees (typical: 0.1 to 180)
     */
    void setFOV(double degrees);

    /**
     * Get current field of view
     */
    double getFOV() const;

    /**
     * Focus view on a celestial object
     *
     * @param objectName Name of object (e.g., "Moon", "Mars", "Tycho")
     */
    void focusObject(const QString& objectName);

    /**
     * Set viewing direction (altitude/azimuth)
     *
     * @param azimuth  Azimuth in degrees (0=North, 90=East)
     * @param altitude Altitude in degrees (0=horizon, 90=zenith)
     */
    void setViewDirection(double azimuth, double altitude);

    // ========== Time Control ==========

    /**
     * Set simulation time (Julian Day)
     *
     * @param jd Julian day number
     */
    void setTime(double jd);

    /**
     * Set simulation time from date/time components
     */
    void setDateTime(int year, int month, int day,
                     int hour, int minute, double second);

    /**
     * Get current simulation time as Julian Day
     */
    double getTime() const;

    // ========== Location ==========

    /**
     * Set observer location on Earth (or Moon)
     *
     * @param latitude  Latitude in degrees (-90 to +90)
     * @param longitude Longitude in degrees (-180 to +180)
     * @param altitude  Altitude in meters above sea level
     * @param planet    Planet name (default: "Earth")
     */
    void setLocation(double latitude, double longitude,
                     double altitude = 0.0,
                     const QString& planet = "Earth");

    // ========== Rendering ==========

    /**
     * Render current view to framebuffer
     *
     * This is the KEY METHOD for seamless integration!
     * Returns direct pointer to pixel data (RGBA format)
     *
     * @return Pointer to framebuffer (width × height × 4 bytes)
     *         Valid until next renderFrame() call
     *         Do NOT free this pointer!
     */
    const unsigned char* renderFrame();

    /**
     * Get rendered frame as QImage (for Qt compatibility)
     */
    QImage getFrameImage();

    /**
     * Save current frame to file (for debugging)
     */
    bool saveFrame(const QString& filename);

    /**
     * Get framebuffer dimensions
     */
    int getWidth() const { return width_; }
    int getHeight() const { return height_; }

    // ========== SONIC-Specific Features ==========

    /**
     * Get list of craters visible in current view
     *
     * This could directly access Stellarium's crater database
     * without rendering, for validation/matching purposes
     *
     * @param minDiameter Minimum crater diameter in km
     * @return Vector of crater positions (to be implemented)
     */
    // std::vector<CraterInfo> getVisibleCraters(double minDiameter = 1.0);

    /**
     * Get Moon phase and illumination
     */
    double getMoonPhase() const;

    /**
     * Check if Moon is currently visible
     */
    bool isMoonVisible() const;

private:
    // Qt offscreen rendering components
    std::unique_ptr<QOffscreenSurface> surface_;
    std::unique_ptr<QOpenGLFramebufferObject> fbo_;
    std::unique_ptr<QOpenGLContext> context_;

    // Stellarium components (would link to actual Stellarium classes)
    // StelApp* stellApp_;
    // StelCore* stellCore_;
    void* stellApp_;   // Placeholder
    void* stellCore_;  // Placeholder

    // Framebuffer info
    int width_;
    int height_;
    bool initialized_;

    // Cached frame data
    unsigned char* frameData_;

    // Internal helpers
    void setupOpenGL();
    void initializeStellariumCore();
    void updateStellariumState();
};

} // namespace sonic
