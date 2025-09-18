const { Romcal } = require('romcal');

(async () => {
  try {
    // change the year below to whatever you need (e.g., 2025)
    const year = 2025;
    const romcal = new Romcal({ scope: 'gregorian' }); // default: General Roman Calendar (GRC)
    const data = await romcal.generateCalendar(year);
    const fs = require('fs');
    fs.writeFileSync(`ordo_${year}.json`, JSON.stringify(data, null, 2), 'utf8');
    console.log(`Wrote ordo_${year}.json — ${data.length} entries`);
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
})();
