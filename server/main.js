const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');
const colors = require('colors');
const db = require('./db');
const config = () => require('./package.json');


const [app, router] = [new Koa(), new Router()];

router.get('/download/:platform', ctx => {
    const platform = parseInt(ctx.params.platform);
    const URL = `http://os3s219a3.bkt.clouddn.com/Luoo.qy-v${config().update.mainVersion}.0.${['dmg', 'exe', 'zip'][platform]}`;
    ctx.redirect(URL);
    log(`/download/${ctx.params.platform}`, ctx.request.ip)
});


router.get('/update/:platform/:preVersion', ctx => {
    const info = config().update;
    const preVersion = ctx.params.preVersion.split('.');

    if (parseInt(preVersion[0]) === info.mainVersion && parseInt(preVersion[1]) === info.updateVersion)
        ctx.body = JSON.stringify({ type: 'none' });

    else if (parseInt(preVersion[0]) !== info.mainVersion)
        ctx.body = JSON.stringify({
            type: 'full',
            version: `${info.mainVersion}.0`,
            url: `http://os3s219a3.bkt.clouddn.com/Luoo.qy-v${info.mainVersion}.0.${['dmg', 'exe', 'zip'][parseInt(ctx.params.platform)]}`,
            desc: info.mainDesc
        });

    else ctx.body = JSON.stringify({
            type: info.type,
            version: `${info.mainVersion}.${info.updateVersion}`,
            url: `http://os3s219a3.bkt.clouddn.com/update-v${info.mainVersion}.${info.updateVersion}.zip`,
            desc: info.updateDesc
        });
    log(`/update/${ctx.params.platform}/${ctx.params.preVersion}`, ctx.request.ip)
});

// 获取所有期刊
router.post('/periods', async ctx => {
    const data = await db.period.get();
    // let arr = data.map(item => item['period_name']);
    ctx.body = JSON.stringify(data || 'error');
    // log(`/single/${ctx.params.date}`, ctx.request.ip)
});

// 获取所有标签
router.post('/labels', async ctx => {
    const data = await db.label.get();
    // let arr = data.map(item => item['label_name']);
    ctx.body = JSON.stringify(data || 'error');
})

router.post('/periodsLabels', async ctx => {
    const data = await db.period.getPeriodsLabels();
    ctx.body = JSON.stringify(data || 'error');
})

// 分页 page  0开始
// pageSize  默认 10
// 获取期刊里面所有专辑
// "period":"r",
// "startId":1
// "endId": 10
// "page":1,
// "pageSize": 3
router.post('/col/period', async ctx => {
    // ctx.body = JSON.stringify(await db.single.getList(parseInt(ctx.params.preDate)));
    // const platform = parseInt(ctx.params.peroid);

    let param = ctx.request.body;
    const data = await db.col.get(param,);
    // let arr = data.map(item => item['label_name']);
    ctx.body = JSON.stringify(data || 'error');
});

// 获取标签下所有的专辑
// "tag":"摇滚",
// "page":1,
// "pageSize": 3
router.post('/col/tag', async ctx => {
    let param = ctx.request.body;
    const data = await db.col.getLabel(param,);
    // let arr = data.map(item => item['label_name']);
    ctx.body = JSON.stringify(data || 'error');
});

// 获取最新的专辑
router.post('/col/lastest', async ctx => {
    const data = await db.col.getLatest();
    ctx.body = JSON.stringify(data || 'error');
});

// 获取专辑里面所有的单曲
// "href":"28",
// "page":1,
// "pageSize": 3
router.post('/singles/col', async ctx => {
    let param = ctx.request.body;
    ctx.body = JSON.stringify(await db.single.getList(param,));
    //log(`/singles/${ctx.params.preDate}`, ctx.request.ip)
});

// 获取首页数据
router.post('/home', async ctx => {
    let param = ctx.request.body;
    ctx.body = JSON.stringify(await db.col.getHome(param,));
});


app.use(bodyParser());
app.use(router.routes()).listen(config().config.port);
app.use(require('koa-static-server')({
    rootDir: path.join(__dirname, '../website'),
    index: 'index.html',
    gzip: true,
    maxage: 1000 * 60 * 60 * 24
}));


function log(api, ip) {
    ip = ip.split(':')[3];
    db.log(api, ip);
    console.log(`Response api  ${api.red}  to  ${ip.yellow}  at  ${(new Date()).toLocaleString().green}`)
}
