
/**
 * 替换数组中的某个元素 并返回一个新数组
 * @param arr 数组
 * @param index 要替换的角标
 * @param newElement 新数据
 */
export function replaceElementToNewArr(arr:[], index:number, newElement:any) {
    return arr.slice(0, index).concat(newElement).concat(arr.slice(index + 1));
}

/**
 * 已知角度 求两个点的坐标（归一化）
 * @param angle 
 * @returns 
 */
 export function calculatePoints(angle) {
    // 将角度转换为弧度
    var angleRad = angle * (Math.PI / 180);

    // 计算点1的坐标
    var x1 = (Math.cos(angleRad) + 1) / 2; // 确保在0到1之间
    var y1 = (Math.sin(angleRad) + 1) / 2; // 确保在0到1之间

    // 计算点2的坐标（与点1角度相差180度）
    var x2 = (Math.cos(angleRad + Math.PI) + 1) / 2; // 确保在0到1之间
    var y2 = (Math.sin(angleRad + Math.PI) + 1) / 2; // 确保在0到1之间

    return [
        { x: x1, y: y1 },
        { x: x2, y: y2 },
    ];
}

/**
 * 已知两个点的坐标，换算成弧度
 * @param x1 
 * @param y1 
 * @param x2 
 * @param y2 
 * @returns 
 */
export function calculateAngle(x1, y1, x2, y2) {
    var deltaX = x2 - x1;
    var deltaY = y2 - y1;
    var angleRad = Math.atan2(deltaY, deltaX);
    var an = radianToDegree(angleRad) + 360;
    return an % 360;
}

/**
 * 将弧度 转换成角度
 * @param radian 弧度
 * @returns 
 */
export function radianToDegree(radian) {
    return Number((radian * (180 / Math.PI)).toFixed(0));
}
