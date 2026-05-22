const { Resend } = require("resend");
const fs = require("fs");
const path = require("path");

const API_URL =
  "https://aareguru.existenz.ch/v2018/current?app=aare-temp&version=1.0.0";
const RECIPIENT = "kevin@holden.ch";

function loadEnv() {
  const envPath = path.join(__dirname, ".env");
  if (!fs.existsSync(envPath)) {
    console.error("Missing .env file. Copy .env.example to .env and add your Resend API key.");
    process.exit(1);
  }
  const lines = fs.readFileSync(envPath, "utf-8").split("\n");
  for (const line of lines) {
    const match = line.match(/^([^=]+)=(.*)$/);
    if (match) process.env[match[1].trim()] = match[2].trim();
  }
}

async function fetchAareData() {
  const res = await fetch(API_URL);
  if (!res.ok) throw new Error(`API returned ${res.status}`);
  return res.json();
}

function findTodayMax(data) {
  const now = new Date();
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startTs = Math.floor(startOfDay.getTime() / 1000);

  const todayReadings = data.aarepast.filter(
    (r) => r.timestamp >= startTs && r.temperature !== null
  );

  if (todayReadings.length === 0) {
    return { max: data.aare.temperature, time: data.aare.timestring, readings: 1 };
  }

  let maxReading = todayReadings[0];
  for (const r of todayReadings) {
    if (r.temperature > maxReading.temperature) maxReading = r;
  }

  const maxTime = new Date(maxReading.timestamp * 1000);
  const timeStr = maxTime.toLocaleTimeString("de-CH", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Europe/Zurich",
  });

  return { max: maxReading.temperature, time: timeStr, readings: todayReadings.length };
}

function buildEmail(maxTemp, maxTime, currentTemp, flow, readings) {
  const today = new Date().toLocaleDateString("de-CH", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "Europe/Zurich",
  });

  let swimVerdict;
  if (maxTemp >= 20) swimVerdict = "Perfect for swimming!";
  else if (maxTemp >= 18) swimVerdict = "Warm enough for a swim.";
  else if (maxTemp >= 16) swimVerdict = "A bit fresh, but doable.";
  else swimVerdict = "Too cold for most swimmers.";

  const subject = `Aare: ${maxTemp.toFixed(1)}°C peak today`;

  const html = `
    <div style="font-family: system-ui, sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color: #1a5276; margin-bottom: 4px;">Aare Marzili — Daily Report</h2>
      <p style="color: #666; margin-top: 0;">${today}</p>

      <div style="background: linear-gradient(135deg, #1a5276, #2e86c1); color: white; border-radius: 12px; padding: 24px; text-align: center; margin: 16px 0;">
        <div style="font-size: 48px; font-weight: bold;">${maxTemp.toFixed(1)}°C</div>
        <div style="font-size: 14px; opacity: 0.9;">Peak temperature at ${maxTime}</div>
      </div>

      <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
        <tr>
          <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Current temperature</td>
          <td style="padding: 8px 0; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">${currentTemp.toFixed(1)}°C</td>
        </tr>
        <tr>
          <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Flow rate</td>
          <td style="padding: 8px 0; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">${flow} m³/s</td>
        </tr>
        <tr>
          <td style="padding: 8px 0;">Measurements today</td>
          <td style="padding: 8px 0; text-align: right; font-weight: bold;">${readings}</td>
        </tr>
      </table>

      <p style="font-size: 16px;">${swimVerdict}</p>

      <p style="color: #999; font-size: 12px; margin-top: 24px;">
        Data from <a href="https://aaremarzili.ch" style="color: #999;">aaremarzili.ch</a> via aare.guru API
      </p>
    </div>
  `;

  return { subject, html };
}

async function main() {
  const dryRun = process.argv.includes("--dry-run");

  loadEnv();

  console.log("Fetching Aare data...");
  const data = await fetchAareData();

  const { max, time, readings } = findTodayMax(data);
  const currentTemp = data.aare.temperature;
  const flow = data.aare.flow;

  console.log(`Today's max: ${max.toFixed(1)}°C at ${time} (${readings} readings)`);
  console.log(`Current: ${currentTemp.toFixed(1)}°C, Flow: ${flow} m³/s`);

  const { subject, html } = buildEmail(max, time, currentTemp, flow, readings);

  if (dryRun) {
    console.log("\n--- DRY RUN ---");
    console.log(`To: ${RECIPIENT}`);
    console.log(`Subject: ${subject}`);
    console.log("Email would be sent. Use 'npm start' to send for real.");
    return;
  }

  const resend = new Resend(process.env.RESEND_API_KEY);

  console.log(`Sending email to ${RECIPIENT}...`);
  const { data: result, error } = await resend.emails.send({
    from: "Aare Temp <aare@holden.ch>",
    to: [RECIPIENT],
    subject,
    html,
  });

  if (error) {
    console.error("Failed to send email:", error);
    process.exit(1);
  }

  console.log(`Email sent! ID: ${result.id}`);
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
