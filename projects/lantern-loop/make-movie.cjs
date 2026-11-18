// Render the same poses and inbetweens as the interactive player.
'use strict';
const {execFileSync} = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const film = require('./film.js');

const fps = 24;
const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'lantern-film-'));
try {
  for (let frame = 0; frame < fps * film.duration; frame++) {
    const drawing = film.frameSVG(film.poseAt(frame / fps), 'film', true)
      .replace('<svg ', '<svg width="900" height="440" ');
    // The close shot looks past the edge of the painted wall. Keep the
    // original player's stage colour visible there when encoding opaque video.
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="900" height="440">
      <rect width="900" height="440" fill="#10292e"/>${drawing}</svg>`;
    fs.writeFileSync(path.join(scratch, String(frame).padStart(3, '0') + '.svg'), svg);
  }

  const rasterizer = path.join(scratch, 'render.swift');
  fs.writeFileSync(rasterizer, `import AppKit
let directory = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
for file in try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
    where file.pathExtension == "svg" {
    try autoreleasepool {
        guard let image = NSImage(contentsOf: file), let tiff = image.tiffRepresentation,
              let bitmap = NSBitmapImageRep(data: tiff),
              let png = bitmap.representation(using: .png, properties: [:]) else {
            throw NSError(domain: "LanternLoop", code: 1,
                          userInfo: [NSLocalizedDescriptionKey: "Could not draw " + file.lastPathComponent])
        }
        try png.write(to: file.deletingPathExtension().appendingPathExtension("png"))
    }
}`);
  execFileSync('swift', ['-module-cache-path', path.join(scratch, 'modules'), rasterizer, scratch],
    {stdio: 'inherit'});
  const movie = path.join(scratch, 'lantern-loop.mp4');
  execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-framerate', String(fps),
    '-i', path.join(scratch, '%03d.png'), '-c:v', 'libx264', '-crf', '18',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', movie], {stdio: 'inherit'});
  fs.copyFileSync(movie, path.join(__dirname, 'lantern-loop.mp4'));
} finally {
  fs.rmSync(scratch, {recursive: true, force: true});
}
