/**
 * SONIC-Stellarium Bridge Implementation
 *
 * This is a PROOF-OF-CONCEPT stub showing the structure.
 * Full implementation would link against actual Stellarium libraries.
 */

#include "sonic_stel_bridge.h"
#include <QOffscreenSurface>
#include <QOpenGLFramebufferObject>
#include <QOpenGLContext>
#include <QOpenGLFunctions>
#include <QImage>
#include <stdexcept>

namespace sonic {

StellariumBridge::StellariumBridge(int width, int height)
    : width_(width)
    , height_(height)
    , initialized_(false)
    , stellApp_(nullptr)
    , stellCore_(nullptr)
    , frameData_(nullptr)
{
}

StellariumBridge::~StellariumBridge()
{
    if (frameData_) {
        delete[] frameData_;
    }
}

bool StellariumBridge::initialize(const QString& configDir)
{
    if (initialized_) {
        return true;
    }

    try {
        // 1. Create OpenGL context
        setupOpenGL();

        // 2. Initialize Stellarium core
        // ACTUAL IMPLEMENTATION would do:
        // stellApp_ = new StelApp();
        // stellApp_->init(configDir);
        // stellCore_ = StelApp::getInstance().getCore();

        // For now: stub
        initializeStellariumCore();

        // 3. Allocate frame buffer
        frameData_ = new unsigned char[width_ * height_ * 4];

        initialized_ = true;
        return true;

    } catch (const std::exception& e) {
        // Handle error
        initialized_ = false;
        return false;
    }
}

void StellariumBridge::setupOpenGL()
{
    // Create OpenGL context for offscreen rendering
    context_ = std::make_unique<QOpenGLContext>();
    context_->create();

    // Create offscreen surface
    surface_ = std::make_unique<QOffscreenSurface>();
    surface_->setFormat(context_->format());
    surface_->create();

    // Make context current
    context_->makeCurrent(surface_.get());

    // Create framebuffer object
    fbo_ = std::make_unique<QOpenGLFramebufferObject>(
        width_,
        height_,
        QOpenGLFramebufferObject::CombinedDepthStencil
    );

    if (!fbo_->isValid()) {
        throw std::runtime_error("Failed to create framebuffer object");
    }
}

void StellariumBridge::initializeStellariumCore()
{
    // STUB: In real implementation, this would:
    // 1. Create StelApp instance
    // 2. Load Stellarium configuration
    // 3. Initialize all Stellarium modules
    // 4. Load sky cultures, landscapes, etc.
    // 5. Set up rendering pipeline

    // Placeholder
    stellApp_ = (void*)0x1;  // Non-null to indicate "initialized"
    stellCore_ = (void*)0x1;
}

void StellariumBridge::updateStellariumState()
{
    // STUB: In real implementation:
    // stellCore_->update(deltaTime);
    // Update all Stellarium modules
}

// ========== View Control ==========

void StellariumBridge::setFOV(double degrees)
{
    // ACTUAL:
    // StelMovementMgr* mvmgr = stellCore_->getMovementMgr();
    // mvmgr->zoomTo(degrees, 0);

    // STUB: Store for later
}

double StellariumBridge::getFOV() const
{
    // ACTUAL:
    // return stellCore_->getMovementMgr()->getCurrentFov();

    return 1.0;  // STUB
}

void StellariumBridge::focusObject(const QString& objectName)
{
    // ACTUAL:
    // StelObjectMgr* objMgr = GETSTELMODULE(StelObjectMgr);
    // objMgr->findAndSelect(objectName);
    // StelMovementMgr* mvmgr = stellCore_->getMovementMgr();
    // mvmgr->setFlagTracking(true);

    // STUB
}

void StellariumBridge::setViewDirection(double azimuth, double altitude)
{
    // ACTUAL:
    // Vec3d v;
    // StelUtils::spheToRect(azimuth * M_PI/180, altitude * M_PI/180, v);
    // stellCore_->getMovementMgr()->setViewDirectionJ2000(stellCore_->altAzToJ2000(v));

    // STUB
}

// ========== Time Control ==========

void StellariumBridge::setTime(double jd)
{
    // ACTUAL:
    // stellCore_->setJD(jd);

    // STUB
}

void StellariumBridge::setDateTime(int year, int month, int day,
                                   int hour, int minute, double second)
{
    // Convert to Julian Day and call setTime()
    // STUB
}

double StellariumBridge::getTime() const
{
    // ACTUAL:
    // return stellCore_->getJD();

    return 2451545.0;  // STUB: J2000.0
}

// ========== Location ==========

void StellariumBridge::setLocation(double latitude, double longitude,
                                   double altitude, const QString& planet)
{
    // ACTUAL:
    // StelLocation loc;
    // loc.latitude = latitude * M_PI/180;
    // loc.longitude = longitude * M_PI/180;
    // loc.altitude = altitude;
    // loc.planetName = planet;
    // stellCore_->moveObserverTo(loc, 0);

    // STUB
}

// ========== Rendering (THE KEY METHOD!) ==========

const unsigned char* StellariumBridge::renderFrame()
{
    if (!initialized_) {
        return nullptr;
    }

    // 1. Make OpenGL context current
    context_->makeCurrent(surface_.get());

    // 2. Bind framebuffer
    fbo_->bind();

    // 3. ACTUAL IMPLEMENTATION would do:
    // stellApp_->prepareFrame();
    // stellApp_->drawPartial();  // Render everything
    // stellApp_->finalizeFrame();

    // STUB: Clear to gradient (simulates rendering)
    QOpenGLFunctions* f = context_->functions();
    f->glViewport(0, 0, width_, height_);
    f->glClearColor(0.0, 0.0, 0.1, 1.0);  // Dark blue
    f->glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // 4. Read pixels from FBO to memory
    QImage img = fbo_->toImage();

    // 5. Copy to our buffer (RGBA format)
    memcpy(frameData_, img.bits(), width_ * height_ * 4);

    // 6. Release FBO
    fbo_->release();

    // 7. Return direct pointer (NO FILE I/O!)
    return frameData_;
}

QImage StellariumBridge::getFrameImage()
{
    if (!initialized_) {
        return QImage();
    }

    renderFrame();  // Ensure frame is rendered

    return QImage(frameData_, width_, height_, QImage::Format_RGBA8888).copy();
}

bool StellariumBridge::saveFrame(const QString& filename)
{
    QImage img = getFrameImage();
    return img.save(filename);
}

// ========== SONIC-Specific ==========

double StellariumBridge::getMoonPhase() const
{
    // ACTUAL:
    // StelObjectMgr* objMgr = GETSTELMODULE(StelObjectMgr);
    // Planet* moon = (Planet*)objMgr->searchByName("Moon");
    // return moon->getPhase(stellCore_->getObserverHeliocentricEclipticPos());

    return 0.5;  // STUB: half moon
}

bool StellariumBridge::isMoonVisible() const
{
    // ACTUAL:
    // Check if Moon is above horizon

    return true;  // STUB
}

} // namespace sonic
