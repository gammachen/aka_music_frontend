<template>
  <div class="prompt-guide">
    <!-- 大纲介绍 -->
    <h1>提示词公式</h1>
    <p>
      提示词用来描述图像中所包含的内容，它是控制画面内容与效果的关键因素。提示词描述越完整、精确和丰富，生成的图像的品质越高，且越贴近期望生成的内容。为了帮助你更快上手，我们针对不同的使用需求提供了两种提示词使用公式。
    </p>

    <!-- 基础公式 -->
    <h2>基础公式</h2>
    <p>适用于初次尝试AI创作的新用户，及将AI作为灵感启发的用户，简单自由的提示词可生成更具有想象力的图像。</p>
    <div class="formula-box">
      <strong>提示词 = 主体 + 场景 + 风格</strong>
      <ul>
        <li><strong>主体：</strong> 主体是图片内容的主要表现对象，可以是人、动物、植物、物品或非物理真实存在的想象之物。</li>
        <li><strong>场景：</strong> 场景是主体所处的环境，包括室内或室外、季节、天气、光线等可以是物理存在的真实空间或想象出来的虚构场景。</li>
        <li><strong>风格：</strong> 选择或定义图像的艺术风格，如写实，抽象等。有助于模型生成具有特定视觉效果的图像。</li>
      </ul>
    </div>

    <!-- 进阶公式 -->
    <h2>进阶公式</h2>
    <p>适用于有一定AI生图使用经验的用户，在基础公式之上添加更丰富细致的描述可有效提升画面质感、细节丰富度与表现力。</p>
    <div class="formula-box">
      <strong>提示词 = 主体（主体描述）+ 场景（场景描述）+ 风格（定义风格）+ 镜头语言 + 氛围词 + 细节修饰</strong>
      <ul>
        <li><strong>主体描述：</strong> 确定主体清晰地描述图像中的主体，包括其特征，动作等。</li>
        <li><strong>场景描述：</strong> 场景描述是对主体所处环境特征细节的描述，可通过形容词或短句列举。</li>
        <li><strong>定义风格：</strong> 定义风格是明确地描述图像所应具有的特定艺术风格、表现手法或视觉特征。</li>
        <li><strong>镜头语言：</strong> 镜头语言包含景别、视角等。</li>
        <li><strong>氛围词：</strong> 氛围词是对预期画面氛围的描述。</li>
        <li><strong>细节修饰：</strong> 细节修饰是对画面进一步的精细化和优化，以增强图像的细节表现力、丰富度和美感。</li>
      </ul>
    </div>

    <!-- 提示词词典 -->
    <h2>提示词词典</h2>
    <p>通过撰写不同维度的提示词，决定了生成图像的内容、风格、细节等多个方面的表现力。</p>

    <!-- 景别分类 -->
    <h3>1. 景别</h3>
    <table>
      <thead>
        <tr>
          <th>景别类型</th>
          <th>提示词示例</th>
          <th>图像效果</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>通用</td>
          <td>通用 | 由羊毛毡制成的大熊猫，头戴大檐帽，穿着蓝色警服马甲，扎着腰带，携带警械装备，戴着蓝手套，穿着皮鞋，大步奔跑姿态，毛毡效果，周围是动物王国城市街道商户，高级滤镜，路灯，动物王国，奇妙童趣，憨态可掬，夜晚，明亮，自然，可爱，4K，毛毡材质，摄影镜头，居中构图，毛毡风格，皮克斯风格，逆光。</td>
          <td><img :src="images[0]" alt="通用示例"></td>
        </tr>
        <tr>
          <td>特写</td>
          <td>特写镜头 | 高清相机，情绪大片，日落，特写人像</td>
          <td><img :src="images[1]" alt="特写示例"></td>
        </tr>
        <tr>
          <td>近景</td>
          <td>近景镜头 | 18岁的中国女孩，古代服饰，圆脸，看着镜头，民族优雅的服装，商业摄影，室外，电影级光照，半身特写，精致的淡妆，锐利的边缘。</td>
          <td><img :src="images[2]" alt="近景示例"></td>
        </tr>
        <tr>
          <td>中景</td>
          <td>中景镜头 | 电影时尚魅力摄影，年轻亚洲女子，中国苗族女孩在，圆脸，看着镜头，民族深色优雅的服装，中广角镜头，阳光明媚，乌托邦式，由高清相机拍摄</td>
          <td><img :src="images[3]" alt="中景示例"></td>
        </tr>
        <tr>
          <td>远景</td>
          <td>远景镜头 | 展示了远景镜头，在壮丽的雪山背景下，两个小小的人影站在远处山顶，背对着镜头，静静地观赏着日落的美景。夕阳的余晖洒在雪山上，呈现出一片金黄色的光辉，与蔚蓝的天空形成鲜明对比。两人仿佛被这壮观的自然景象所吸引，整个画面充满了宁静与和谐。</td>
          <td><img :src="images[4]" alt="远景示例"></td>
        </tr>
        <tr>
          <td>平视</td>
          <td>平视视角 | 图像展示了从平视视角捕捉到的草地景象。一群羊悠闲地在绿茵茵的草地上低头觅食，它们的羊毛在早晨微弱的阳光照耀下呈现出温暖的金色光泽，形成美丽的光影效果。</td>
          <td><img :src="images[5]" alt="平视示例"></td>
        </tr>
        <tr>
          <td>俯视</td>
          <td>俯视视角 | 我从空中俯瞰冰湖，中心有一艘小船，周围环绕着漩涡图案和充满活力的蓝色海水。螺旋深渊，该场景是从上方自上而下的视角拍摄的，展示了复杂的细节，例如表面的波纹和积雪覆盖的地面下的层。眺望冰冷的广阔天地。营造出一种令人敬畏的宁静静感。</td>
          <td><img :src="images[6]" alt="俯视示例"></td>
        </tr>
        <tr>
          <td>仰视</td>
          <td>仰视视角 | 展示了热带地区的壮观景象，高大的椰子树如同参天巨人般耸立，枝叶茂盛，直指蓝天。镜头采用仰视视角，让观众仿佛置身树下，感受大自然的雄伟与生机。阳光透过树叶间隙洒落，形成斑驳光影，增添了几分神秘与浪漫。整个画面充满了热带风情，让人仿佛能闻到椰香，感受到微风拂面的惬意。</td>
          <td><img :src="images[7]" alt="仰视示例"></td>
        </tr>
        <tr>
          <td>航拍</td>
          <td>航拍 | 展示了大雪，村庄，道路，灯火，树木。。</td>
          <td><img :src="images[8]" alt="航拍示例"></td>
        </tr>
      </tbody>
    </table>

    <!-- 视角分类 -->
    <h3>2. 视角</h3>
    <table>
      <thead>
        <tr>
          <th>视角类型</th>
          <th>提示词示例</th>
          <th>图像效果</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>微距</td>
          <td>樱桃 | 新鲜的红色樱桃，带有水滴，背景为黑色，突显其鲜艳的颜色和光泽。professional color grading, clean sharp focus, commercial high quality, magazine winning photography, hyper realistic, uhd, 8K</td>
          <td><img :src="images[9]" alt="樱桃示例"></td>
        </tr>
        <tr>
          <td>超广角</td>
          <td>雪景小镇 | 冬季的小镇，房屋被白雪覆盖，灯光温暖，道路蜿蜒，树木和山丘构成美丽的风景。碧海蓝天下的海岛，阳光透过树叶缝隙，洒下斑驳光影。</td>
          <td><img :src="images[10]" alt="雪景小镇示例"></td>
        </tr>
        <tr>
          <td>长焦</td>
          <td>长焦镜头 | 豹子在森林中，背景模糊，突出豹子的斑点和锐利的眼神。长焦镜头下，一只猎豹在郁郁葱葱的森林中站立，面对镜头，背景被巧妙地虚化，猎豹的面部成为画面的绝对焦点。阳光透过树叶的缝隙，洒在猎豹身上，形成斑驳的光影效果，增强了视觉冲击力。</td>
          <td><img :src="images[11]" alt="豹子示例"></td>
        </tr><tr>
          <td>鱼眼</td>
          <td>鱼眼镜头 | 鱼眼镜头的特殊视角下，一位女性站立着并直视镜头的场景。她的形象在画面中心被夸张地放大，四周则呈现出强烈的扭曲效果，营造出一种独特的视觉冲击力。</td>
          <td><img :src="images[12]" alt="鱼眼镜头"></td>
        </tr>
      </tbody>
    </table>

    <!-- 风格分类 -->
    <h3>3. 风格</h3>
    <table>
      <thead>
        <tr>
          <th>风格</th>
          <th>提示词示例</th>
          <th>图像效果</th>
        </tr>
      </thead>
      <tbody>
        <!-- 添加风格示例的内容 -->
        <tr>
          <td>3D卡通</td>
          <td>网球女运动员，短发，白色网球服，黑色短裤，侧身回球，3D卡通风格。</td>
          <td><img :src="images[13]" alt="3D卡通示例"></td>
        </tr>
        <tr>
          <td>废土风</td>
          <td>火星上的城市，废土风格。</td>
          <td><img :src="images[14]" alt="废土风示例"></td>
        </tr>
        <tr>
          <td>点彩画</td>
          <td>一座白色的小房子，茅草房，一片被雪覆盖的草原，大胆使用点彩色画，莫奈感，清晰的笔触，边缘模糊，原始的边缘纹理，低饱和度的颜色，低对比度，莫兰迪色。</td>
          <td><img :src="images[15]" alt="点彩画示例"></td>
        </tr>
        <tr>
          <td>超现实</td>
          <td>深灰色大海中一条粉红色的发光河流，具有极简、美丽和审美的氛围，具有超现实风格的电影灯光。</td>
          <td><img :src="images[16]" alt="超现实示例"></td>
        </tr>
        <tr>
          <td>水彩</td>
          <td>咖啡馆外，明亮的白色背景，更少细节，梦幻，吉卜力工作室。</td>
          <td><img :src="images[17]" alt="超现实示例"></td>
        </tr>
        <tr>
          <td>粘土</td>
          <td>，蓝色毛衣的小男孩，棕色卷发，深蓝色贝雷帽，画板，户外，海边，半身照。</td>
          <td><img :src="images[18]" alt="超现实示例"></td>
        </tr>
        <tr>
          <td>写实</td>
          <td>篮子，葡萄，野餐布，超写实静物摄影，微距镜头，丁达尔效应。</td>
          <td><img :src="images[19]" alt="写实示例"></td>
        </tr>
        <tr>
          <td>陶瓷</td>
          <td>展示了高细节的瓷器小狗，它静静地躺在桌上，脖子上系着一个精致的铃铛。小狗的每一根毛发都被细腻地刻画出来，眼睛、鼻子和嘴巴的细节栩栩如生。</td>
          <td><img :src="images[20]" alt="陶瓷示例"></td>
        </tr>
        <tr>
          <td>3D</td>
          <td>中国龙，可爱的中国龙睡在白云上，迷人的花园，在晨雾中，特写，正面，3D立体，C4D渲染，32k超高清，32k UHD，中国朋克，32k UHD，动物雕像，辛烷值渲染，超高清晰度。</td>
          <td><img :src="images[21]" alt="3D示例"></td>
        </tr>
        <tr>
          <td>水墨</td>
          <td>兰花，水墨画，留白，意境，吴冠中风格，细腻的笔触，宣纸的纹理。</td>
          <td><img :src="images[22]" alt="水墨示例"></td>
        </tr>
        <tr>
          <td>折纸</td>
          <td>折纸杰作，牛皮纸材质的熊猫，森林背景，中景，极简主义，背光，最佳品质。</td>
          <td><img :src="images[23]" alt="折纸示例"></td>
        </tr>
        <tr>
          <td>工笔</td>
          <td>晨曦中，一枝寒梅傲立雪中，花瓣细腻如丝，露珠轻挂，展现工笔画之精致美。</td>
          <td><img :src="images[24]" alt="工笔示例"></td>
        </tr>
        <tr>
          <td>国风水墨</td>
          <td>国风水墨风格，一个长长的黑发男人，金色的发髻，飞舞着金色的蝴蝶，白色的服装，高细节，高质量，深蓝色背景，背景中有若隐若现的水墨竹林。</td>
          <td><img :src="images[25]" alt="国风水墨示例"></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'PromptGuide',
  data() {
    return {
      images: [
        '/prompt/image1.png',
        '/prompt/image2.png',
        '/prompt/image3.png',
        '/prompt/image4.png',
        '/prompt/image5.png',
        '/prompt/image6.png',
        '/prompt/image7.png',
        '/prompt/image8.png',
        '/prompt/image9.png',
        '/prompt/image10.png',
        '/prompt/image11.png',
        '/prompt/image12.png',
        '/prompt/image13.png',
        '/prompt/image14.png',
        '/prompt/image15.png',
        '/prompt/image16.png',
        '/prompt/image17.png',
        '/prompt/image18.png',
        '/prompt/image19.png',
        '/prompt/image20.png',
        '/prompt/image21.png',
        '/prompt/image22.png',
        '/prompt/image23.png',
        '/prompt/image24.png',
        '/prompt/image25.png',
        '/prompt/image26.png',
        '/prompt/image27.png'
      ]
    };
  }
}

</script>

<style scoped>
.prompt-guide {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.formula-box {
  background-color: #f0f8ff;
  padding: 10px;
  margin-bottom: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed; /* 确保表格列宽固定 */
}

table, th, td {
  border: 1px solid #ddd;
}

th, td {
  padding: 8px;
  text-align: left;
  vertical-align: top; /* 确保内容顶部对齐 */
}

th {
  background-color: #f2f2f2;
}

img {
  width: 150px; /* 统一图片宽度 */
  height: auto; /* 保持图片比例 */
  display: block; /* 确保图片居中 */
  margin: 0 auto; /* 确保图片居中 */
}

/* 统一三列宽度 */
table th:nth-child(1),
table td:nth-child(1) {
  width: 20%;
}

table th:nth-child(2),
table td:nth-child(2) {
  width: 50%;
}

table th:nth-child(3),
table td:nth-child(3) {
  width: 30%;
}
</style>