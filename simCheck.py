import cv2

def simCheck(img1, img2):

    image_one = cv2.imread(img1)
    image_two = cv2.imread(img2)

    result = ""
    #Check if two images are equals
    if image_one.shape == image_two.shape:
        difference = cv2.subtract(image_one, image_two)
        b, g, r = cv2.split(difference)

        if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
            result = "Good similarity"
        else:
            result = "Bad similarity"

    #Check similarities between the 2 images
    sift = cv2.xfeatures2d.SIFT_create()
    kp_1, desc_1 = sift.detectAndCompute(image_one, None)
    kp_2, desc_2 = sift.detectAndCompute(image_two, None)

    index_params = dict(algorithm=0, trees=5)
    search_params = dict()
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(desc_1, desc_2, k=2)

    good_points = []
    for m, n in matches:
        if m.distance < 0.6*n.distance:
            good_points.append(m)

    # Define how similar they are
    number_keypoints = 0
    if len(kp_1) <= len(kp_2):
        number_keypoints = len(kp_1)
    else:
        number_keypoints = len(kp_2)

    #print("Keypoints Image one: " + str(len(kp_1)))
    #print("Keypoints Image two: " + str(len(kp_2)))
    #print("Good Matches:", len(good_points))
    if number_keypoints == 0:
        print("Match: 0/100")
        result = "Bad similarity"
    else:
        print("Match: ", len(good_points) / number_keypoints * 100, "/100")
        if len(good_points) / number_keypoints * 100 > 10:
            result = "Good similarity"
        else:
            result = "Bad similarity"
    print(result)

    return result
