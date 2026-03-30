---
name: link-button
description: link 中的按钮相关功能
metadata:
  author: moushu
---

link-button 默认有节流功能，默认情况 0.5s 内只会触发一次

```vue
<link-button label="主按钮" color="primary" @click="点击事件"/>
<link-button label="次按钮" @click="点击事件"/>
<link-button label="文字" type="none" @click="点击事件"/>

<link-button label="按钮" icon="link-icon-down"/>
<link-button label="按钮（右侧）" icon="link-icon-down" iconPosition="right"/>
```

| 属性名称 | 类型 | 可选值 | 默认值 | 说明 |
| ---- | ---- | ---- | ---- | ---- |
| type | String | line, fill, none | fill | 按钮类型 |
| color | String | primary, success, warn, error, info | info | 按钮颜色 |
| size | String | large, default, small | default | 按钮大小 |
| shape | String | round, none, fillet | none | 按钮形状 |
| label | String | — | — | 按钮文本 |
| icon | String | — | — | 按钮图标 |
| iconLoading | Boolean | — | — | 按钮图标是否处于loading状态 |
| iconPosition | String | — | — | 按钮图标位置 |
| iconOnly | Boolean | — | — | 按钮是否只显示图标 |
| long | Boolean | — | — | 是否为长按钮(占满一行) |
| noBorder | Boolean | — | — | 是否去除按钮边框 |
| noPadding | Boolean | — | — | 是否去除按钮默认内边距 |
| node | String | — | button | 按钮节点 |
| preventFastClickDuration | — | — | 500 | 节流，在这个事件范围内，按钮被多次点击只会派发一次click事件 |
| availableTimes | — | — | — | 按钮可点击次数 |
| loading | Boolean | — | — | 按钮是否处于loading状态 |
| synchronize | Boolean | — | true | 按钮是否开启自动异步控制，使用该用能，按钮的click函数句柄必须返回一个promise对象或者使用async关键字修饰函数 |
| buttonType | String | — | button | 按钮类型，如果希望在表单中点击自动提交，则设置为submit |
| active | Boolean | — | — | 按钮是否处于激活状态 |
