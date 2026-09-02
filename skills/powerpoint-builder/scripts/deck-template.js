// Generic editable PowerPoint template. Copy to working/ and replace placeholders.
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = process.env.PRESENTATION_AUTHOR || "";
pptx.company = process.env.PRESENTATION_COMPANY || "";
pptx.subject = "{{SUBJECT}}";
pptx.title = "{{TITLE}}";
pptx.lang = "ja-JP";
pptx.theme = {
  headFontFace: "Yu Gothic UI",
  bodyFontFace: "Yu Gothic UI",
  lang: "ja-JP",
};

const C = {
  dark: "1E2761",
  section: "101E4B",
  primary: "1E2761",
  accent: "0F6CBD",
  pale: "F5F7FB",
  white: "FFFFFF",
  text: "3A4A6B",
  muted: "616A82",
  line: "E4E7EF",
  lightBlue: "8FB3E0",
};
const W = 13.333;
const H = 7.5;
const FONT = "Yu Gothic UI";
const GENERATED_DIR = process.env.PRESENTATION_GENERATED_DIR || "working/images/generated";
const ICON_DIR = process.env.PRESENTATION_ICON_DIR || "working/images/icons";

function localImage(baseDir, name) {
  if (!name) return "";
  const root = path.resolve(baseDir);
  const candidate = path.resolve(root, name);
  if (candidate !== root && !candidate.startsWith(root + path.sep)) {
    throw new Error(`image must be under ${baseDir}: ${name}`);
  }
  if (!fs.existsSync(candidate)) throw new Error(`image not found: ${candidate}`);
  return candidate;
}

function imageDimensions(fileName) {
  const data = fs.readFileSync(fileName);
  if (data.length >= 24 && data.toString("ascii", 1, 4) === "PNG") {
    return { width: data.readUInt32BE(16), height: data.readUInt32BE(20) };
  }
  if (data.length >= 4 && data[0] === 0xff && data[1] === 0xd8) {
    let offset = 2;
    while (offset + 9 < data.length) {
      if (data[offset] !== 0xff) { offset += 1; continue; }
      const marker = data[offset + 1];
      if ([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf].includes(marker)) {
        return { width: data.readUInt16BE(offset + 7), height: data.readUInt16BE(offset + 5) };
      }
      if (marker === 0xd8 || marker === 0xd9) { offset += 2; continue; }
      const length = data.readUInt16BE(offset + 2);
      if (length < 2) break;
      offset += length + 2;
    }
  }
  if (path.extname(fileName).toLowerCase() === ".svg") {
    const source = data.toString("utf8", 0, Math.min(data.length, 16384));
    const viewBox = source.match(/viewBox=["']\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)\s*["']/i);
    if (viewBox) return { width: Number(viewBox[1]), height: Number(viewBox[2]) };
    const width = source.match(/\bwidth=["']([\d.]+)(?:px)?["']/i);
    const height = source.match(/\bheight=["']([\d.]+)(?:px)?["']/i);
    if (width && height) return { width: Number(width[1]), height: Number(height[1]) };
  }
  throw new Error(`unsupported image dimensions: ${fileName}`);
}

function coverRight(fileName, x, y, w, h) {
  const dimensions = imageDimensions(fileName);
  const scale = Math.max(w / dimensions.width, h / dimensions.height);
  const imageW = dimensions.width * scale;
  const imageH = dimensions.height * scale;
  return { path: fileName, x: x + w - imageW, y: y + (h - imageH) / 2, w: imageW, h: imageH };
}

function addLocalIcon(slide, fileName, x, y, size, label) {
  if (!fileName) return;
  const image = localImage(ICON_DIR, fileName);
  slide.addImage({ path: image, x, y, w: size, h: size });
  if (label) {
    slide.addText(label, {
      x: x - 0.18, y: y + size + 0.08, w: size + 0.36, h: 0.28,
      fontFace: FONT, fontSize: 10, color: C.text, align: "center", margin: 0,
    });
  }
}

function addTitle(slide, title, lead = "") {
  slide.addText(title, {
    x: 0.65, y: 0.38, w: 12.03, h: 0.55,
    fontFace: FONT, fontSize: 28, bold: true, color: C.dark, margin: 0,
  });
  if (lead) {
    slide.addText(lead, {
      x: 0.65, y: 1.05, w: 12.03, h: 0.55,
      fontFace: FONT, fontSize: 14, color: C.muted, margin: 0,
    });
  }
}

function addCard(slide, x, y, w, h, number, title, body, imageName = "") {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: C.white }, line: { color: C.line, width: 0.75 },
  });
  const imageHeight = 1355889 / 914400;
  if (imageName) {
    slide.addImage({
      path: localImage(GENERATED_DIR, imageName),
      x, y: y + 80000 / 914400, w, h: imageHeight,
    });
  }
  const contentY = imageName ? y + 80000 / 914400 + imageHeight : y + 0.35;
  slide.addShape(pptx.ShapeType.ellipse, {
    x: x + 0.26, y: contentY + 0.18, w: 0.42, h: 0.42,
    fill: { color: C.accent }, line: { color: C.accent },
  });
  slide.addText(String(number), {
    x: x + 0.26, y: contentY + 0.18, w: 0.42, h: 0.42,
    fontFace: FONT, fontSize: 10, bold: true, color: C.white,
    align: "center", valign: "mid", margin: 0,
  });
  slide.addText(title, {
    x: x + 0.82, y: contentY + 0.18, w: w - 1.08, h: 0.42,
    fontFace: FONT, fontSize: 16, bold: true, color: C.dark, margin: 0,
  });
  slide.addShape(pptx.ShapeType.line, {
    x: x + 0.26, y: contentY + 0.76, w: w - 0.52, h: 0,
    line: { color: C.line, width: 0.75 },
  });
  const bodyY = contentY + 0.95;
  slide.addText(body, {
    x: x + 0.28, y: bodyY, w: w - 0.5, h: y + h - bodyY - 0.2,
    fontFace: FONT, fontSize: 14, color: C.text, margin: 0, valign: "top",
  });
}

function addSectionDivider(slide, imageName, title, accent = "", subtitle = "") {
  slide.background = { color: C.section };
  if (imageName) {
    const image = localImage(GENERATED_DIR, imageName);
    slide.addImage(coverRight(image, 0, 0, W, H));
    const steps = 16;
    const blendW = W * 0.58;
    for (let index = 0; index < steps; index += 1) {
      const stripW = blendW / steps + 0.01;
      slide.addShape(pptx.ShapeType.rect, {
        x: index * blendW / steps, y: 0, w: stripW, h: H,
        fill: { color: C.section, transparency: Math.round(100 * index / (steps - 1)) },
        line: { color: C.section, transparency: 100 },
      });
    }
  }
  slide.addText([
    { text: title, options: { color: C.white, bold: true } },
    { text: accent, options: { color: C.lightBlue, bold: true } },
  ], {
    x: 0.75, y: 1.45, w: 5.5, h: 1.65,
    fontFace: FONT, fontSize: 38, margin: 0, breakLine: false,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.75, y: 3.35, w: 5.25, h: 0.8,
      fontFace: FONT, fontSize: 16, color: C.white, margin: 0,
    });
  }
}

function addSource(slide, source) {
  if (!source) return;
  slide.addText(`出典: ${source}`, {
    x: 0.65, y: 7.05, w: 12.03, h: 0.2,
    fontFace: FONT, fontSize: 8.5, italic: true, color: C.white, margin: 0,
  });
}

const cover = pptx.addSlide();
const coverImage = process.env.PRESENTATION_COVER_IMAGE || "";
addSectionDivider(cover, coverImage, "{{TITLE}}", "", "{{SUBTITLE}}");
cover.addText("{{DATE}}", {
  x: 0.75, y: 5.85, w: 5.25, h: 0.35,
  fontFace: FONT, fontSize: 14, color: C.white, margin: 0,
});
cover.addNotes("{{COVER_NOTES}}");

const summary = pptx.addSlide();
summary.background = { color: C.pale };
addTitle(summary, "{{SUMMARY_TITLE}}", "{{SUMMARY_LEAD}}");
const cardLeft = 457200 / 914400;
const cardGap = 200000 / 914400;
const cardWidth = 3615706 / 914400;
const cardY = 1597999 / 914400;
const cardH = 4205287 / 914400;
addCard(summary, cardLeft, cardY, cardWidth, cardH, 1, "{{POINT_1_TITLE}}", "{{POINT_1_BODY}}", process.env.PRESENTATION_CARD_IMAGE_1 || "");
addCard(summary, cardLeft + cardWidth + cardGap, cardY, cardWidth, cardH, 2, "{{POINT_2_TITLE}}", "{{POINT_2_BODY}}", process.env.PRESENTATION_CARD_IMAGE_2 || "");
addCard(summary, cardLeft + 2 * (cardWidth + cardGap), cardY, cardWidth, cardH, 3, "{{POINT_3_TITLE}}", "{{POINT_3_BODY}}", process.env.PRESENTATION_CARD_IMAGE_3 || "");
summary.addShape(pptx.ShapeType.rect, {
  x: 0, y: 6048632 / 914400, w: W, h: 561368 / 914400,
  fill: { color: C.dark }, line: { color: C.dark },
});
addLocalIcon(summary, process.env.PRESENTATION_ICON_1 || "", 1.0, 5.15, 0.42, "{{ICON_1_LABEL}}");
addLocalIcon(summary, process.env.PRESENTATION_ICON_2 || "", 5.1, 5.15, 0.42, "{{ICON_2_LABEL}}");
addLocalIcon(summary, process.env.PRESENTATION_ICON_3 || "", 9.18, 5.15, 0.42, "{{ICON_3_LABEL}}");
addSource(summary, "{{SUMMARY_SOURCE}}");
summary.addNotes("{{SUMMARY_NOTES}}");

const output = process.argv[2] || "working/presentation.pptx";
pptx.writeFile({ fileName: output })
  .then(() => console.log(`WROTE: ${output}`))
  .catch((error) => { console.error(error); process.exitCode = 1; });
