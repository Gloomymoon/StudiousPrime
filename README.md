# StudiousPrime

### version 0.5 material-design
updated 2016-11-26
**Happy Black Friday!**

1 切换为Material Design主题

2 业务类重构

3 增加选词功能

### version 0.4
updated 2016-11-19

**Happy Thanksgiving!**

1 增加了部分缺失的第三方js和css文件

2 增加了测试题目数量设置功能

3 增加了用户登录页面

### version 0.3
updated 2016-11-18

1 修改了部分config，使用本地jquery和boostrap css库

2 修改了部分页面细节样式，优化列表的点击，返回按钮能够返回之前浏览的分页

3 去除了单词的Book_id关联，question增加level属性

4 增加了首页累计成绩图

### version 0.2
updated 2016-11-05

1 增加Achievements页面

2 增加首页新词和错误最多的5个词

3 修复部分bug

4 调整单词评分：答错不扣分

5 答题增加判断：不允许在有未填字符的情况下提交

### version 0.1 
updated 2016-11-03

1 分用户，一个录入新学单词（或词组），一个进行练习，架构上已经考虑多用户分权限的扩展性

2 单词需要如下属性字段：

* 单词或词组的英文
* 中文解释（以后可通过网络爬取）
* 例句（以后可通过网络爬取），建议可以支持图片展示
* 评分，答对+1，答错-1，不可为负

3 词库说明
 新录入单词评分为0，按照评分对单词分等级
* lvl-1 新学单词，评分为0-2
* lvl-2 近期单词，评分为3-4
* lvl-3 近期熟练单词，评分5-6
* lvl-4 长期单词，评分7-9
* lvl-5 永久记忆库，评分10及以上，5级单词不会再次测试，但是其数量可以作为一个成就

4 练习题生成逻辑
* lvl-1，从低分到高分顺序选取10个，分数相同随机
* lvl-2，随机选取5个
* lvl-3，随机选取5个
* lvl-4，随机选取5个
如果该等级题量不够则从下一等级选取

5 练习题测试逻辑
* 每个单词随机展现有限个字母，总长5个及以下单词随机展示1个字母，6个及以上随机展现2个，10个以上展现3个，未展现的字母用下划线“_”标识，空格永远显示
* 显示中文解释
* 点击[例句]，显示例句，例句中该单词用*代替

6 评分
* 每次全部练习后反馈当天的分数，并展示所有错误的单词
* 后台记录每天测试情况

7 查看（Todo）
* 查看每日练习数量、总得分、平均得分
* 查看每日累计掌握单词量
* 查看错误单词排行(done)
* 查看词库等级分布(done)
