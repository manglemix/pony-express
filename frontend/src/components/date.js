const dateHelper = dateHelperFactory();
export const formatMe = date => {
    date = new Date(date);
  // const vals = `yyyy,mm,dd,hh,mmi,ss,mms`.split(`,`);
  const vals = `yyyy,mm,dd,hh,mmi`.split(`,`);
  const myDate = dateHelper(date).toArr(...vals);
  return `${myDate.slice(0, 3).join(`/`)} ${
    myDate.slice(3, 6).join(`:`)}`;
};

function dateHelperFactory() {
  const padZero = (val, len = 2) => `${val}`.padStart(len, `0`);
  const setValues = date => {
    let vals = {
       yyyy: date.getFullYear(),
       m: date.getMonth()+1,
       d: date.getDate(),
       h: date.getHours(),
       mi: date.getMinutes(),
      //  s: date.getSeconds(),
      //  ms: date.getMilliseconds(),
      };
    Object.keys(vals).filter(k => k !== `yyyy`).forEach(k => 
      // vals[k[0]+k] = padZero(vals[k], k === `ms` && 3 || 2)
      vals[k[0]+k] = padZero(vals[k], 2)
    );
    return vals;
  };
  
  return date => ( {
    values: setValues(date),
    toArr(...items) { return items.map(i => this.values[i]); },
  } );
}