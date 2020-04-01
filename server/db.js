const fs = require('node-fs-extra');
const db = require('mongodb').MongoClient;
const config = () => fs.readJSONFileSync('./package.json').config;


module.exports = {
    // 期
    period: {
        get: getPeriods
    },
    // 期详情
    col: {
    },
    // 单曲
    single: {
        latest: getLatestSingle,
        get: getSingle,
        getList: getSingleList
    },
    // 标签
    label: {
        get: getLabels
    },
    log: writeLog
};


let col, single, log, period, label;
db.connect('mongodb://localhost:27017/luoow', function (error, db) {
    if (error) throw new Error(error);
    col = db.collection('col');
    single = db.collection('single');
    log = db.collection('log');
    period = db.collection('period');
    label = db.collection('label');
});


function writeLog(api, ip) {
    const date = new Date();
    if (!api || !ip) return;
    log.insert({ api, ip, date })
}


function getVol(volNum) {
    return new Promise((resolve, reject) => {
        if (config().disappearVols.includes(vol))
            return false;
        let retryTimes = 0;
        let timer;
        if (!col)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (vol) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        col.find({vol: parseInt(volNum)}).toArray((error, doc) => {
            if (error) reject(error);
            resolve(doc.length > 0 ? doc[0] : false)
        })
    }
}


function getVolList(preVol) {
    return new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!col)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (vol) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        col.find({vol: { $gt: parseInt(preVol), $lt: getLatestVol() + 1 }})
            .toArray(async (error, doc) => {
                if (error) reject(error);
                for (let j=0; j<doc.length; j++)
                    doc[j].tracks = await getTracks(parseInt(doc[j].vol))
                resolve(doc)
        })
    }
}


function getSingle(date) {
    return new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!single)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (single) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        single.find({date: parseInt(date)}).toArray((error, doc) => {
            if (error) reject(error);
            resolve(doc.length > 0 ? doc[0] : false)
        })
    }
}


function getSingleList(preDate) {
    return new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!single)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (single) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        single.find({date: { $gt: parseInt(preDate), $lt: getLatestSingle() + 1 }})
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(doc)
        })
    }
}

function getLatestVol() {
    return config().latestVol
}

function getLatestSingle() {
    return config().latestSingle
}

function getPeriods() {
    return new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!period)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (single) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        period.find()
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(doc)
        })
    }
}

function getLabels() {
    return new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!label)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (single) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        // var f = label.find().toArray()
        // console.log(f)
        label.find()
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(doc)
        })
    }
}