const { Romcal } = require('romcal');
const fs = require('fs');

(async () => {
  try {
    const year = 2025; // change this to whichever year you want
    const romcal = new Romcal({ scope: 'gregorian' }); // default: General Roman Calendar (GRC)

    // generate the calendar with readings included
    const data = await romcal.generateCalendar(year, { includeReadings: true });

    // write the JSON to file
    const outputPath = `ordo_${year}_readings.json`;
    fs.writeFileSync(outputPath, JSON.stringify(data, null, 2), 'utf8');

    console.log(`Wrote ${outputPath} — ${Object.keys(data).length} days`);
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
})();

