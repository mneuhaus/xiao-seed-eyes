#include <vector>
#include <string>
#include <TFT_eSPI.h>
#include <SPI.h>
#include <SD.h>
#include <math.h>
#include <algorithm>
#include <WiFi.h>
#include <WebServer.h>

WebServer server(80);




#ifdef ARDUINO_ARCH_RP2350
#undef PICO_BUILD
#endif
#include "AnimatedGIF.h"

AnimatedGIF gif;
TFT_eSPI tft = TFT_eSPI();

// rule: loop GIF at least during 3s, maximum 5 times, and don't loop/animate longer than 30s per GIF
const int maxLoopIterations =     1; // stop after this amount of loops
const int maxLoopsDuration  =  3000; // ms, max cumulated time after the GIF will break loop
const int maxGifDuration    =240000; // ms, max GIF duration

// used to center image based on GIF dimensions
static int xOffset = 0;
static int yOffset = 0;

static int totalFiles = 0; // GIF files count
static int currentFile = 0;
static int lastFile = -1;

char GifComment[256];

static File FSGifFile; // temp gif file holder
static File GifRootFolder; // directory listing
std::vector<std::string> GifFiles; // GIF files path
static File uploadFile; // file upload handler
#define DISPLAY_WIDTH 240

static void MyCustomDelay( unsigned long ms ) {
  delay( ms );
  // log_d("delay %d\n", ms);
}

static void * GIFOpenFile(const char *fname, int32_t *pSize)
{
  // log_d("GIFOpenFile( %s )\n", fname );
  FSGifFile = SD.open(fname);
  if (FSGifFile) {
    *pSize = FSGifFile.size();
    return (void *)&FSGifFile;
  }
  return NULL;
}

static void GIFCloseFile(void *pHandle)
{
  File *f = static_cast<File *>(pHandle);
  if (f != NULL)
     f->close();
}

static int32_t GIFReadFile(GIFFILE *pFile, uint8_t *pBuf, int32_t iLen)
{
  int32_t iBytesRead;
  iBytesRead = iLen;
  File *f = static_cast<File *>(pFile->fHandle);
  // Note: If you read a file all the way to the last byte, seek() stops working
  if ((pFile->iSize - pFile->iPos) < iLen)
      iBytesRead = pFile->iSize - pFile->iPos - 1; // <-- ugly work-around
  if (iBytesRead <= 0)
      return 0;
  iBytesRead = (int32_t)f->read(pBuf, iBytesRead);
  pFile->iPos = f->position();
  return iBytesRead;
}

static int32_t GIFSeekFile(GIFFILE *pFile, int32_t iPosition)
{
  int i = micros();
  File *f = static_cast<File *>(pFile->fHandle);
  f->seek(iPosition);
  pFile->iPos = (int32_t)f->position();
  i = micros() - i;
  // log_d("Seek time = %d us\n", i);
  return pFile->iPos;
}

static void TFTDraw(int x, int y, int w, int h, uint16_t* lBuf )
{
  tft.pushRect( x+xOffset, y+yOffset, w, h, lBuf );
}

// Draw a line of image directly on the LCD
void GIFDraw(GIFDRAW *pDraw)
{
  uint8_t *s;
  uint16_t *d, *usPalette, usTemp[320];
  int x, y, iWidth;

  iWidth = pDraw->iWidth;
  if (iWidth > DISPLAY_WIDTH)
      iWidth = DISPLAY_WIDTH;
  usPalette = pDraw->pPalette;
  y = pDraw->iY + pDraw->y; // current line

  s = pDraw->pPixels;
  if (pDraw->ucDisposalMethod == 2) {// restore to background color
    for (x=0; x<iWidth; x++) {
      if (s[x] == pDraw->ucTransparent)
          s[x] = pDraw->ucBackground;
    }
    pDraw->ucHasTransparency = 0;
  }
  // Apply the new pixels to the main image
  if (pDraw->ucHasTransparency) { // if transparency used
    uint8_t *pEnd, c, ucTransparent = pDraw->ucTransparent;
    int x, iCount;
    pEnd = s + iWidth;
    x = 0;
    iCount = 0; // count non-transparent pixels
    while(x < iWidth) {
      c = ucTransparent-1;
      d = usTemp;
      while (c != ucTransparent && s < pEnd) {
        c = *s++;
        if (c == ucTransparent) { // done, stop
          s--; // back up to treat it like transparent
        } else { // opaque
            *d++ = usPalette[c];
            iCount++;
        }
      } // while looking for opaque pixels
      if (iCount) { // any opaque pixels?
        TFTDraw( pDraw->iX+x, y, iCount, 1, (uint16_t*)usTemp );
        x += iCount;
        iCount = 0;
      }
      // no, look for a run of transparent pixels
      c = ucTransparent;
      while (c == ucTransparent && s < pEnd) {
        c = *s++;
        if (c == ucTransparent)
            iCount++;
        else
            s--;
      }
      if (iCount) {
        x += iCount; // skip these
        iCount = 0;
      }
    }
  } else {
    s = pDraw->pPixels;
    // Translate the 8-bit pixels through the RGB565 palette (already byte reversed)
    for (x=0; x<iWidth; x++)
      usTemp[x] = usPalette[*s++];
    TFTDraw( pDraw->iX, y, iWidth, 1, (uint16_t*)usTemp );
  }
} /* GIFDraw() */

int gifPlay( char* gifPath )
{ // 0=infinite
  gif.begin(BIG_ENDIAN_PIXELS);
  if( ! gif.open( gifPath, GIFOpenFile, GIFCloseFile, GIFReadFile, GIFSeekFile, GIFDraw ) ) {
    // log_n("Could not open gif %s", gifPath );
    return maxLoopsDuration;
  }

  int frameDelay = 0; // store delay for the last frame
  int then = 0; // store overall delay
  bool showcomment = false;

  // center the GIF !!
  int w = gif.getCanvasWidth();
  int h = gif.getCanvasHeight();
  xOffset = ( tft.width()  - w )  /2;
  yOffset = ( tft.height() - h ) /2;

  if( lastFile != currentFile ) {
    // log_n("Playing %s [%d,%d] with offset [%d,%d]", gifPath, w, h, xOffset, yOffset );
    lastFile = currentFile;
    showcomment = true;
  }

  while (gif.playFrame(true, &frameDelay)) {
    if( showcomment )
      if (gif.getComment(GifComment))
        // log_n("GIF Comment: %s", GifComment);
    then += frameDelay;
    if( then > maxGifDuration ) { // avoid being trapped in infinite GIF's
      // log_w("Broke the GIF loop, max duration exceeded");
      break;
    }
  }

  gif.close();
  return then;
}

int getGifInventory( const char* basePath )
{
  int amount = 0;
  GifRootFolder = SD.open(basePath);
  if(!GifRootFolder){
    // log_n("Failed to open directory");
    return 0;
  }

  if(!GifRootFolder.isDirectory()){
    // log_n("Not a directory");
    return 0;
  }

  File file = GifRootFolder.openNextFile();

  tft.setTextColor( TFT_WHITE, TFT_BLACK );
  tft.setTextSize( 2 );

  int textPosX = tft.width()/2 - 16;
  int textPosY = tft.height()/2 - 10;

  tft.drawString("GIF Files:", textPosX-40, textPosY-20 );

  while( file ) {
    if(!file.isDirectory()) {
      GifFiles.push_back(std::string(file.name()));
      amount++;
      tft.drawString(String(amount), textPosX, textPosY );
      file.close();
    }
    file = GifRootFolder.openNextFile();
  }
  GifRootFolder.close();
  // log_n("Found %d GIF files", amount);
  return amount;
}

String getGifInventoryApi(const char* basePath) {
  String json = "[";
  File root = SD.open(basePath);
  if(!root || !root.isDirectory()){
    return json + "]";
  }
  File file = root.openNextFile();
  bool first = true;
  while(file) {
    if(!file.isDirectory()){
      if(!first) {
        json += ",";
      }
      json += "\"" + String(file.name()) + "\"";
      first = false;
    }
    file = root.openNextFile();
  }
  root.close();
  json += "]";
  return json;
}

void handleFileUpload() {
  HTTPUpload& upload = server.upload();
  if(upload.status == UPLOAD_FILE_START) {
    if(SD.exists(upload.filename)) {
      SD.remove(upload.filename);
    }
    uploadFile = SD.open(upload.filename, FILE_WRITE);
  } else if(upload.status == UPLOAD_FILE_WRITE) {
    if(uploadFile)
      uploadFile.write(upload.buf, upload.currentSize);
  } else if(upload.status == UPLOAD_FILE_END) {
    if(uploadFile)
      uploadFile.close();
  }
}

void setup() {
  tft.begin();
  tft.setRotation(2);
  tft.fillScreen(TFT_BLACK);

  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  
  const char* ssid = "neuhaus.nrw";
  const char* password = "galactic.poop.bear";
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("Web API Ready", tft.width()/2 - 70, tft.height()/2);

  server.on("/", []() {
    String gifListHtml = "";
    File root = SD.open("/gif");
    if (root && root.isDirectory()) {
      Serial.println("DEBUG: Successfully opened /gif directory for scanning.");
      File file = root.openNextFile();
      while (file) {
        Serial.print("DEBUG: Processing file: ");
        Serial.println(file.name());
        if (!file.isDirectory()) {
          String fname = file.name();
          if (fname.endsWith(".gif") || fname.endsWith(".GIF")) {
            Serial.print("DEBUG: Found GIF file: ");
            Serial.println(fname);
          }
          gifListHtml += "<button class='btn btn-secondary m-1' onclick=\"sendCommand('/playgif?name=" + fname + "')\">" + fname + "</button>";
        }
        file = root.openNextFile();
      }
      Serial.println("DEBUG: Completed /gif directory scan.");
      root.close();
    } else {
      Serial.println("DEBUG: Failed to open /gif directory.");
    }
    String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>TFT_eSPI GifPlayer API</title>";
    html += "<link rel=\"stylesheet\" href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css\">";
    html += "</head><body><div class=\"container mt-4\">";
    if (server.hasArg("upload") && server.arg("upload") == "success") {
      html += "<div class='alert alert-success' role='alert'>Upload successful</div>";
    }
    html += "<h1 class=\"mb-4\">Welcome to the TFT_eSPI GifPlayer API</h1>";
    html += "<h2>Commands</h2>";
    html += "<div class=\"mb-4\">";
    html += "<button class=\"btn btn-primary mb-2\" onclick=\"sendCommand('/open')\">Open</button><br>";
    html += "<button class=\"btn btn-primary mb-2\" onclick=\"sendCommand('/close')\">Close</button><br>";
    html += "<button class=\"btn btn-primary mb-2\" onclick=\"sendCommand('/blink')\">Blink</button><br>";
    html += "<button class=\"btn btn-primary mb-2\" onclick=\"sendCommand('/colorful')\">Colorful</button><br>";
    html += "</div>";
    html += "<h2>Available GIFs</h2>";
    html += "<div class='mb-4'>" + gifListHtml + "</div>";
    html += "<h2>Upload GIF</h2>";
    html += "<form method='POST' action='/upload' enctype='multipart/form-data' class='mb-4'>";
    html += "<div class='form-group'>";
    html += "<label for='file'>Select GIF file:</label>";
    html += "<input type='file' name='file' class='form-control-file' id='file'>";
    html += "</div>";
    html += "<button type='submit' class='btn btn-primary'>Upload</button>";
    html += "</form>";
    html += "<script>function sendCommand(cmd){fetch(cmd).then(response=>response.text()).then(text=>console.log(text));}</script>";
    html += "</div></body></html>";
    server.send(200, "text/html", html);
  });
  server.on("/open", []() {
    tft.fillScreen(TFT_BLACK);
    tft.fillCircle(tft.width()/2, tft.height()/2, 50, TFT_WHITE);
    tft.fillCircle(tft.width()/2, tft.height()/2, 30, TFT_BLUE);
    tft.fillCircle(tft.width()/2, tft.height()/2, 10, TFT_BLACK);
    server.send(200, "text/plain", "Executed command: open");
  });
  server.on("/close", []() {
    tft.fillScreen(TFT_BLACK);
    tft.drawLine(tft.width()/2 - 50, tft.height()/2, tft.width()/2 + 50, tft.height()/2, TFT_WHITE);
    tft.drawLine(tft.width()/2 - 50, tft.height()/2 + 1, tft.width()/2 + 50, tft.height()/2 + 1, TFT_WHITE);
    server.send(200, "text/plain", "Executed command: close");
  });
  server.on("/blink", []() {
    tft.fillScreen(TFT_BLACK);
    tft.drawLine(tft.width()/2 - 50, tft.height()/2, tft.width()/2 + 50, tft.height()/2, TFT_WHITE);
    delay(200);
    tft.fillScreen(TFT_BLACK);
    tft.fillCircle(tft.width()/2, tft.height()/2, 50, TFT_WHITE);
    tft.fillCircle(tft.width()/2, tft.height()/2, 30, TFT_BLUE);
    tft.fillCircle(tft.width()/2, tft.height()/2, 10, TFT_BLACK);
    server.send(200, "text/plain", "Executed command: blink");
  });
  server.on("/colorful", []() {
    unsigned long time = millis();
    for (int yPos = 0; yPos < tft.height(); yPos += 10) {
      for (int xPos = 0; xPos < tft.width(); xPos += 10) {
        float wave = sin((xPos + time / 10.0) * 0.05) + cos((yPos + time / 10.0) * 0.05);
        uint16_t color = tft.color565(
          (int)((sin(wave + time / 1000.0) + 1) * 127.5),
          (int)((cos(wave + time / 1000.0) + 1) * 127.5),
          (int)(((sin(wave) + cos(wave)) / 2 + 1) * 127.5)
        );
        tft.fillRect(xPos, yPos + (int)(10 * sin((xPos + time / 100.0) * 0.1)), 10, 10, color);
      }
    }
    server.send(200, "text/plain", "Executed command: colorful");
  });

  server.on("/gifs", []() {
    String json = getGifInventoryApi("/");
    server.send(200, "application/json", json);
  });
  server.on("/playgif", []() {
    if (server.hasArg("name")) {
      String gifName = server.arg("name");
      int playTime = gifPlay(const_cast<char*>(gifName.c_str()));
      server.send(200, "text/plain", "Playing gif: " + gifName);
    } else {
      server.send(400, "text/plain", "Missing gif name");
    }
  });
  server.on("/upload", HTTP_GET, []() {
    String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Upload GIF</title>";
    html += "<link rel=\"stylesheet\" href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css\">";
    html += "</head><body><div class=\"container mt-4\">";
    html += "<h1>Upload GIF</h1>";
    html += "<form method='POST' action='/upload' enctype='multipart/form-data'>";
    html += "<div class='form-group'>";
    html += "<label for='file'>Select GIF file:</label>";
    html += "<input type='file' name='file' class='form-control-file' id='file'>";
    html += "</div>";
    html += "<button type='submit' class='btn btn-primary'>Upload</button>";
    html += "</form>";
    html += "</div></body></html>";
    server.send(200, "text/html", html);
  });
  server.on("/upload", HTTP_POST, []() {
    server.sendHeader("Location", "/?upload=success");
    server.send(302, "text/plain", "");
  }, handleFileUpload);
  server.begin();
  Serial.println("HTTP server started");
  delay(2000);
}



void loop() {
  server.handleClient();
  delay(1);
}

