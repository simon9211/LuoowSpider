const fs = require('node-fs-extra');
const db = require('mongodb').MongoClient;
const config = () => fs.readJSONFileSync('./package.json').config;


module.exports = {
    // 期
    period: {
        get: getPeriods,
        getPeriodsLabels: getPeriodsAndLabels
    },
    // 期详情
    col: {
        get: getCols,
        getLabel: getLabelCols,
        getLatest: getLatestCols,
        getHome: getHomeCols,
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
                if (period) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        period.find({period_name: /^vol./}, { '_id': 0 }).map(item => item["period_name"])
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(doc)
            })
    }
}

function getPeriodsAndLabels() {
    var promise = new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!period)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (period) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    var promise1 = new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!label)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (label) {
                    exec1(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec1(resolve, reject)
    });

    return Promise.all([promise, promise1]).then(posts => {
        // Promise.resolve()
        return {'data':{'periods':posts[0],'labels':posts[1]}};
    }).catch(function (reason) {
        // ...
    });

    function exec(resolve, reject) {
        period.find({period_name: /^vol./}, { '_id': 0 }).map(item => item["period_name"])
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(doc)
            })
    }

    function exec1(resolve, reject) {
        label.find({}, { '_id': 0 }).map(item => item["label_name"])
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
                if (label) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        // var f = label.find().toArray()
        // console.log(f)
        label.find({}, { '_id': 0 }).map(item => item["label_name"])
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
                if (col) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        var col_id;
        if (p.period == 'e' || p.period == 'r') {
            // -1 其他
            //  0 音乐电台
            col_id = p.period == 'e' ? -1 : 0;
            col.find({ col_id: col_id }, { '_id': 0, 'col_id': 0 }).sort({ href: 1, _id: -1 })
                .toArray(async (error, doc) => {
                    if (error) reject(error);
                    resolve(handlePage(doc, p));
                })
        } else {
            // "startId":1
            // "endId": 10
            let startId = parseInt(p.startId), endId = parseInt(p.endId);
            col.find({ col_id: { '$gte': startId, '$lte': endId } }, { '_id': 0, 'col_id': 0 }).sort({ href: 1, _id: -1 })
                .toArray(async (error, doc) => {
                    if (error) reject(error);
                    resolve(handlePage(doc, p));
                })
        }
    }
}

// 查询含有该标签的所有专辑
function getLabelCols(p) {
    return new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!col)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (col) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        col.find({ tags: p.tag }, { '_id': 0 }).sort({ title: 1, _id: -1 })
            .toArray((error, doc) => {
                if (error) reject(error);
                resolve(handlePage(doc, p));
            })
    }
}

function getHomeCols(p) {
    var promise = new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!col)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (col) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    var promise1 = new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!col)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (col) {
                    exec1(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec1(resolve, reject)
    });

    var promise2 = new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!col)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (col) {
                    exec2(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec2(resolve, reject)
    });

    return Promise.all([promise, promise1, promise2]).then(posts => {
        // Promise.resolve()
        return {'data':{'r':posts[0],'e':posts[1],'n':posts[2]}};
    }).catch(function (reason) {
        // ...
    });

    function exec(resolve, reject) {
        //  0 音乐电台
        var res = {};
        col.find({ col_id: 0 }, { '_id': 0, 'col_id': 0,}).sort({ href: 1, _id: -1 })
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(resolveResponse(doc, 10));
            })
    }

    function exec1(resolve, reject) {
        // -1 其他
        col.find({ col_id: -1 }, { '_id': 0 }).sort({ title: 1, _id: -1 })
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(resolveResponse(doc, 10));
            })
    }

    function exec2(resolve, reject) {
        col.find({}, { '_id': 0 }).sort({ title: 1, _id: -1 })
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(resolveResponse(doc, 10));
            })
    }
}

function resolveResponse(doc, n) {
    if (doc.length < n) {
        return doc;
    } else {
        var res = [];
        for (let index = doc.length - n; index < doc.length; index++) {
            res.push(doc[index]);
        }
        return res;
    }
}

// 查询最新的专辑 10条
function getLatestCols() {
    return new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!col)
            timer = setInterval(function () {
                if (retryTimes > config().maxRetryTimes)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (col) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    });

    function exec(resolve, reject) {
        col.find({}, { '_id': 0 }).sort({ title: 1, _id: -1 })
            .toArray((error, doc) => {
                if (error) reject(error);
                if (doc.length < 10) {
                    resolve({ 'data': doc });
                } else {
                    var res = [];
                    for (let index = doc.length - 10; index < doc.length; index++) {
                        res.push(doc[index]);
                    }
                    resolve({ 'data': res });
                }
            })
    }
}

// 查询专辑下所有的单曲
function getSingleList(p) {
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
        single.find({ href: p.href }, { '_id': 0 }).sort({ src: 1, _id: -1 })
            .toArray(async (error, doc) => {
                if (error) reject(error);
                resolve({ 'data': doc,});
            })
    }
}

// 处理分页
function handlePage(doc, query) {
    let page = query.page != undefined ? parseInt(query.page) : 0;
    let pageSize = query.pageSize != undefined ? parseInt(query.pageSize) : 10;
    var arr = [];
    if (doc.length < page * pageSize) {
        for (let index = 0; index < pageSize; index++) {
            arr.push(doc[index])
        }
    } else {
        for (let index = page * pageSize; index < page * pageSize + pageSize; index++) {
            arr.push(doc[index])
        }
    }

    return { 'data': arr, 'totalCount': doc.length, 'currentPage': page };
}