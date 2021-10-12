import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
from skimage import measure, color, io
from skimage.segmentation import clear_border
import glob


pixels_to_um = 0.5 # 1 pixel = 500 nm (got this from the metadata of original image)

propList = ['Area', #Alan
            'equivalent_diameter', #Eş değer Çap
            'orientation', #X ekseni ve ana eksen arasındaki açı.
            'MajorAxisLength', #Anaeksen uzunluğu
            'MinorAxisLength', #Minör eksen uzunluğu
            'Perimeter', #Çevre
            'MinIntensity', #minimum yoğunluk
            'MeanIntensity', #ortalama yoğunluk
            'MaxIntensity']  #maximium yoğunluk
output_file = open('cell_couting_numlabel.csv', 'w')  #Yazılabilir CSV dosyamız

output_file.write('FileName' + "," + 'Cell Number '+  "," + ",".join(propList) + '\n' + '\n')

path = "hucreler/*.jpg"

for file in glob.glob(path): #Görüntülere ulaşmak için oluşturduğumuz for döngüsü
    print(file)     #Konsola okunan dosya yazılıyor
    img1= cv2.imread(file) #Görüntüyü okuyoruz
    cv2.imshow("Orginal Image", img1)
    img = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY) #Gri tonlamaya döndürüyoruz
    ret1, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    kernel = np.ones((3,3),np.uint8)
    opening1 = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
    dilated = cv2.dilate(opening1, kernel, iterations=1)

#Threshold işleminden sonra 8 bit olan görüntümüzü boolean yani binary yapıyoruz.
#Array içindeki her değer için eğer değeri 255 olan her pixel için TRUE, 0 olan için FALSE değerini atıyor
    mask = dilated == 255
    io.imshow(mask)

    c_mask = clear_border(mask)

#Bu işlemlerden sonra hücremiz arka plandan ayrılıyor ve hücreleri işaretlemeye başlıyoruz
#Scipy içindeki ndimage paketindeki label fonksiyonu ile her hücre ayrı bir id ile işaretleniyor
#Birbirlerine 1 px dahi bağlı olan hücreleri bir hücre olarak sayıyor, yani birbirine bağlı olmayan hücreleri etiketliyor, belirliyor.


#structure parametresi etiketlenenler için connectivty tanımlar yani hangi hücrelerin(pixellerin) birbirinden bağımsız olduğunu yada olmadığını belirler
# Yani bir pixelin diğerine bağlı olup olmadığını bulmada kullanılı. Etiketleme işinde ise bağlı oluğ olmama durumu etkilidir.
#İmageJ'deki gibi önerilen yöntem olan 8 con. kullanılmıştır.
#s değerimiz 8connectivity için. Bunun sonucunda diyagnol yani çapraz pixelleride katıyoruz.
#Default bırakırsan bu değer [[0, 1, 0], [1, 1, 1], [0, 1, 0]] yani 4connectivity olur.
    s = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

# Bu işlemden sonra tüm hücreler işaretlenmiş olacak
    labeled_mask, num_labels = ndimage.label(c_mask, structure=s)

#Rasgele renkler ile hücreleri renklendiriyor
#işaretlenmiş olan labeled_mask
#bg rengini 0 yaptık
    img2 = color.label2rgb(labeled_mask, bg_label=0)

 # Görüntünün farklı hallerinin görüntülenmesi
    cv2.imshow("Thresholded Image",thresh)
    cv2.imshow("Opened Image",opening1)
   # cv2.imshow("Masked Image", mask)
   # cv2.imshow("Clean Borders", c_mask)
    cv2.imshow('Colored Grains', img2)
    cv2.waitKey(0)
#etiketli olan resimler için bu işlemi yapıyro
#orginal olarak img da veriyoruz çünkü işlemler için
    clusters = measure.regionprops(labeled_mask, img)

    grain_number = 1  # Başlangıç olarak verdiğimiz hücre sayımız çünkü altta hemen 1 yazıyorum ondan dolayı
    for cluster_props in clusters:
        # output cluster properties to the excel file
        output_file.write(str(cluster_props['Label']))
        for i, prop in enumerate(propList):
            if (prop == 'Area'):
                to_print = cluster_props[prop] * pixels_to_um ** 2  # Convert pixel square to um square
            elif (prop == 'orientation'):
                to_print = cluster_props[prop] * 57.2958  # Convert to degrees from radians
            elif (prop.find('Intensity') < 0):  # Any prop without Intensity in its name
                to_print = cluster_props[prop] * pixels_to_um
            else:
                to_print = cluster_props[prop]  # Reamining props, basically the ones with Intensity in its name
            output_file.write(',' + str(to_print))
        output_file.write('\n')
        grain_number += 1  # Yeni hücreye geçiş ile hücre sayısı artıyor.1
    print(file, "Goruntusunde", grain_number - 1, "adet hücre sayildi.")  # Konsol Çıktıları
    output_file.write(
        file + " GORUNTUSUNDE " + str(grain_number - 1) + " ADET HUCRE SAYILDI. " + '\n' + '\n')  # Konsol Çıktıları

output_file.close()  # Dosyayı kapatıyoruzki read only olmasın
