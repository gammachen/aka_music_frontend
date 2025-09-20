/**
 * 图片压缩工具类
 */
export class ImageCompressor {
  /**
   * 压缩图片
   * @param file 图片文件
   * @param options 压缩选项
   * @returns Promise<Blob> 压缩后的图片Blob对象
   */
  static async compress(file: File, options: {
    maxWidth?: number;
    maxHeight?: number;
    quality?: number;
    mimeType?: string;
  } = {}): Promise<Blob> {
    const {
      maxWidth = 1920,
      maxHeight = 1080,
      quality = 0.8,
      mimeType = 'image/jpeg'
    } = options;

    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          try {
            const compressedBlob = this.compressImage(img, {
              maxWidth,
              maxHeight,
              quality,
              mimeType
            });
            resolve(compressedBlob);
          } catch (error) {
            reject(error);
          }
        };
        img.onerror = () => {
          reject(new Error('图片加载失败'));
        };
        img.src = e.target?.result as string;
      };
      reader.onerror = () => {
        reject(new Error('文件读取失败'));
      };
      reader.readAsDataURL(file);
    });
  }

  /**
   * 使用Canvas压缩图片
   * @param img Image对象
   * @param options 压缩选项
   * @returns Blob 压缩后的图片Blob对象
   */
  private static compressImage(img: HTMLImageElement, options: {
    maxWidth: number;
    maxHeight: number;
    quality: number;
    mimeType: string;
  }): Blob {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Canvas context 创建失败');
    }

    // 计算压缩后的尺寸
    let { width, height } = img;
    if (width > options.maxWidth || height > options.maxHeight) {
      const ratio = Math.min(
        options.maxWidth / width,
        options.maxHeight / height
      );
      width *= ratio;
      height *= ratio;
    }

    // 设置Canvas尺寸
    canvas.width = width;
    canvas.height = height;

    // 绘制图片
    ctx.drawImage(img, 0, 0, width, height);

    // 转换为Blob
    const dataURL = canvas.toDataURL(options.mimeType, options.quality);
    const binaryString = atob(dataURL.split(',')[1]);
    const len = binaryString.length;
    const arr = new Uint8Array(len);

    for (let i = 0; i < len; i++) {
      arr[i] = binaryString.charCodeAt(i);
    }

    return new Blob([arr], { type: options.mimeType });
  }

  /**
   * 将Blob转换为Base64
   * @param blob Blob对象
   * @returns Promise<string> Base64字符串
   */
  static async blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        resolve(reader.result as string);
      };
      reader.onerror = () => {
        reject(new Error('Blob转Base64失败'));
      };
      reader.readAsDataURL(blob);
    });
  }
}

// 使用示例：
/*
// 压缩图片
const compressImage = async (file: File) => {
  try {
    const compressedBlob = await ImageCompressor.compress(file, {
      maxWidth: 1920,
      maxHeight: 1080,
      quality: 0.8
    });
    
    // 如果需要Base64格式
    const base64 = await ImageCompressor.blobToBase64(compressedBlob);
    
    return { blob: compressedBlob, base64 };
  } catch (error) {
    console.error('图片压缩失败:', error);
    throw error;
  }
};
*/