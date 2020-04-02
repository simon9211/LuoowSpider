const fs = require('node-fs-extra');
const db = require('mongodb').MongoClient;
const config = () => fs.readJSONFileSync('./package.json').config;


module.exports = {
    // 期
    period: {
        get: getPeriods,
    },
    // 期详情
    col: {
        get: getCols,
        getLabel: getLabelCols
    },
    // 单曲
    single: {
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
        col.find({ vol: parseInt(volNum) }).toArray((error, doc) => {
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
        col.find({ vol: { $gt: parseInt(preVol), $lt: getLatestVol() + 1 } })
            .toArray(async (error, doc) => {
                if (error) reject(error);
                for (let j = 0; j < doc.length; j++)
                    doc[j].tracks = await getTracks(parseInt(doc[j].vol))
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


// 查询所有的期刊
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
        period.find({}, { '_id': 0 })
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(doc)
            })
    }
}

// 查询所有的标签
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
        label.find({}, { '_id': 0 })
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(doc)
            })
    }
}

// 查询某一期所有的专辑
function getCols(p) {
    return new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!col)
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
        var col_id;
        if (p == 'e' || p == 'r') {
            // -1 其他
            //  0 音乐电台
            col_id = p == 'e' ? -1 : 0;
            col.find({ col_id: col_id}, { '_id': 0, 'col_id': 0 }).sort({href:1, _id:-1})
                .toArray(async (error, doc) => {
                    if (error) reject(error);
                    resolve(doc)
                })
        } else {
            col_id = parseInt(p);
            col.find({ col_id: { '$gte': col_id, '$lte': col_id + 99 } }, { '_id': 0, 'col_id': 0 }).sort({href:1, _id:-1})
                .toArray(async (error, doc) => {
                    if (error) reject(error);
                    resolve(doc)
                })
        }
    }
}

// 查询含有该标签的所有专辑
function getLabelCols(label) {
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
        col.find({ tags:label }, { '_id': 0 }).sort({title:1, _id:-1})
        .toArray((error, doc) => {
            if (error) reject(error);
            resolve(doc)
        })
    }
}

// 查询专辑下所有的单曲
function getSingleList(href) {
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
        single.find({ href:href }, { '_id': 0 }).sort({src:1, _id:-1})
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(doc)
            })
    }
}