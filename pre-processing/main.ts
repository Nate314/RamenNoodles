import { readFileSync, writeFileSync } from 'fs';

const input: string = '../ramen-ratings.csv';
const output: string = '../ramen-ratings.json';

type RamenRecord = { ReviewNum: number, Brand: string, Variety: string,
    Style: string, Country: string, Stars: number, TopTen: number };

function csvToJson(): RamenRecord[] {
    // read csv
    const ramenratingscsv: string = readFileSync(input).toString();
    // format into list of RamenRecord
    const records: RamenRecord[] = ramenratingscsv.split('\n').map(line => {
        const parts = line.split(',');
        return <RamenRecord> {
            ReviewNum: Number(parts[0]),
            Brand: parts[1],
            Variety: parts[2],
            Style: parts[3],
            Country: parts[4],
            Stars: Number(parts[5]),
            TopTen: Number(parts[6])
        };
    });
    // sort by review number and filter out dud records
    return records.sort((a, b) => a.ReviewNum < b.ReviewNum ? -1 : 1).filter(x => !!x.ReviewNum);
}

function replaceOneOffsWithOther(ramenratings: RamenRecord[]): RamenRecord[] {
    // returns brand names that have more than one RamenRecord in the list passed
    function getBrands(ramenratings: RamenRecord[]): string[] {
        const makeobj = (b, c) => ({Brand: b, Count: c});
        const result = [...new Set(ramenratings.map(x => x.Brand))]
            .map(brand => makeobj(brand, ramenratings.filter(x => x.Brand === brand).length));
        const other = makeobj('Other', result.filter(x => x.Count === 1).length);
        return result
            .filter(x => x.Count !== 1).concat([other])
            .sort((a, b) => a.Count < b.Count ? 1 : -1)
            .map(x => x.Brand);
    }
    const brands: string[] = getBrands(ramenratings);
    // replace the Brand name to 'Other' if the brand name did not appear more than once
    return ramenratings.map(x => {
        x.Brand = brands.indexOf(x.Brand) === -1 ? 'Other' : x.Brand;
        return x;
    });
}

function replaceVarietyWith100MostCommonWords(ramenratings: RamenRecord[]): RamenRecord[] {
    // list of all words contained in all Variety labels from the list of RamenRecord passed
    const allwords: string[] = ramenratings.map(x => x.Variety).reduce((total, x) => `${total} ${x}`).split(' ').filter(x => !!x);
    // list of the 100 most common words
    const mostCommonWords: string[] = [...new Set(
        allwords.map(x => ({Word: x, Count: allwords.filter(y => y === x).length}))
            .sort((a, b) => a.Count < b.Count ? 1 : -1).map(x => JSON.stringify(x))
    )].map(x => JSON.parse(x)).splice(0, 100).map(x => x.Word);
    // return the RamenRecord array passed, but only keep the most common words in the Variety labels
    return ramenratings.map(x => {
        const commonWords = x.Variety.split(' ')
            .filter(x => mostCommonWords.indexOf(x) !== -1);
        x.Variety = commonWords.length === 0 ? '' : commonWords.reduce((total, x) => `${total} ${x}`);
        return x;
    });
}

// transform the data from csv to json,
// rename one off companies to 'Other',
// and only keep the 100 most common words in the Variety labels
const ramenratings: RamenRecord[] = replaceVarietyWith100MostCommonWords(replaceOneOffsWithOther(csvToJson()));
// write the output to a .json file
writeFileSync(output, JSON.stringify(ramenratings));
