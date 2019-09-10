import os, sys, re, cv2, math, numpy as np, requests, jsonpickle

DEBUG = False

# Gets the rgb paths for the 885 pngs
def get_rgb_paths(dataset_dir_path):
	# rgb filename regex
	reg_str = r'^pcd(\d{4})r\.png$'
	reg = re.compile(reg_str)

	# Goes through dirs
	path_list = []
	for root, dirs, files in os.walk(dataset_dir_path):
		# Gets all rgb images and sorts by image number
		if files:
			files_rgb = [f for f in files if reg.match(f)]
			if files_rgb:
				files_rgb.sort(key=lambda x: int(reg.match(x).group(1)))
				path_list += [os.path.join(root, f) for f in files_rgb]

	# Sorts by dir number 01-10 and returns
	if path_list:
		path_list.sort(key=lambda x: int(x.split(os.sep)[-2]))
	return path_list

# Gets rectangle file paths for pos/neg
def get_rec_paths(dataset_dir_path):
	# rec filename regex
	reg_str_pos = r'^pcd(\d{4})cpos\.txt$'
	reg_str_neg = r'^pcd(\d{4})cneg\.txt$'
	reg_pos = re.compile(reg_str_pos)
	reg_neg = re.compile(reg_str_neg)

	# Goes through dirs
	path_list_pos = []
	path_list_neg = []
	for root, dirs, files in os.walk(dataset_dir_path):
		# Gets all rgb images and sorts by image number
		if files:
			files_pos = [f for f in files if reg_pos.match(f)]
			files_neg = [f for f in files if reg_neg.match(f)]
			if files_pos:
				files_pos.sort(key=lambda x: int(reg_pos.match(x).group(1)))
				path_list_pos += [os.path.join(root, f) for f in files_pos]
			if files_neg:
				files_neg.sort(key=lambda x: int(reg_neg.match(x).group(1)))
				path_list_neg += [os.path.join(root, f) for f in files_neg]

	# Sorts by dir number 01-10 and returns
	if path_list_pos:
		path_list_pos.sort(key=lambda x: int(x.split(os.sep)[-2]))
	if path_list_neg:
		path_list_neg.sort(key=lambda x: int(x.split(os.sep)[-2]))
	return path_list_pos, path_list_neg

# Find valid rectangle points from gt files and store to list
def find_rec_points(path):
	with open(path) as gtf:
		# Goes through positive points
		rec_pts = []
		rec_list = []
		for num, line in enumerate(gtf):
			# Gets point, converts to float tuple, and stores it
			line_split = line.strip('\n').split(' ')
			point = tuple([float(p) for p in line_split[:2]])
			rec_pts.append(point)

			# Checks if last rectangle point or not
			if num != 0 and (num+1) % 4 == 0:
				# Adds rectangle to list if no NaNs and sets nan flag
				nan_flag = False
				for ps in rec_pts:
					for p in ps:
						if math.isnan(p):
							nan_flag = True
							break
					if nan_flag:
						break

				# Checks for NaN's to discard and adds if not
				if not nan_flag:
					rec_list.append(rec_pts)
				rec_pts = []

		# Returns rectangles
		return rec_list

# Makes ground truth dictionary
# Key is rgb file path and contains dicts for pos/neg with 3d list of rectangle points
def make_gt_dict(path_list_rgb, path_list_pos, path_list_neg):
	# Goes through all rgb/recs
	gt_dict = {}
	for path_rgb, path_pos, path_neg in zip(path_list_rgb, path_list_pos, path_list_neg):
		# Gets all valid positive and negative rectangles
		pos_rec_list, neg_rec_list = find_rec_points(path_pos), find_rec_points(path_neg)

		# Adds recs to gt_dict
		gt_dict.update({
			path_rgb : {
				'pos' : pos_rec_list,
				'neg' : neg_rec_list
			}
		})

	# Returns ground truth dictionary
	return gt_dict

# Creates visualization of ground truth pos/neg rectangles
def create_vis(vis_dir_path, gt_dict, incl_negs=False):
	# rgb filename regex
	reg_str = r'^pcd(\d{4})r\.png$'
	reg = re.compile(reg_str)

	# Goes through rgb images
	for rgb_path, rec_dict in gt_dict.items():
		# Opens image
		img = cv2.imread(rgb_path, -1)

		# Draws pos recs green bgr
		color = (0, 255, 0)
		for rec in rec_dict['pos']:
			if len(rec) < 4: print(rgb_path, rec)
			p1, p2, p3, p4 = [(round(r[0]), round(r[1])) for r in rec]
			cv2.line(img, p1, p2, color)
			cv2.line(img, p2, p3, color)
			cv2.line(img, p3, p4, color)
			cv2.line(img, p4, p1, color)

		# Draws neg recs red bgr
		if incl_negs:
			color = (0, 0, 255)
			for rec in rec_dict['neg']:
				p1, p2, p3, p4 = [(round(r[0]), round(r[1])) for r in rec]
				cv2.line(img, p1, p2, color)
				cv2.line(img, p2, p3, color)
				cv2.line(img, p3, p4, color)
				cv2.line(img, p4, p1, color)

		# Checks vis path
		if not os.path.exists(vis_dir_path):
			os.makedirs(vis_dir_path)

		# Saves vis
		path, fname = os.path.split(rgb_path)
		fnum = reg.match(fname).group(1)
		fname = f'pcd{fnum}vis.png'
		out_path = os.path.join(vis_dir_path, fname)
		cv2.imwrite(out_path, img)

	# Completed successfully
	return True

# Uploads to Detectron
def upload(url, frame):
	# Prep headers for http req
	content_type = 'application/json'
	headers = {'content_type': content_type}

	# jsonpickle the numpy frame
	_, frame_png = cv2.imencode('.png', frame)
	frame_json = jsonpickle.encode(frame_png)

	# Post and get response
	try:
		response = requests.post(url, data=frame_json, headers=headers)
		if response.text:
			# Decode response and return it
			retList = jsonpickle.decode(response.text)
			retList[0] = cv2.imdecode(retList[0], cv2.IMREAD_COLOR)
			retList[-1] = [cv2.imdecode(m, cv2.IMREAD_GRAYSCALE) for m in retList[-1]]
			
			# returns [vis.png, bbList, labelList, scoreList, maskList]
			return retList
		else:
			return None
	except:
		return None

# Creates masks for all 885 rgb pngs using FAIR Detectron/Mask R-CNN
def create_masks(gt_dict):
	# rgb filename regex
	reg_str = r'^pcd(\d{4})r\.png$'
	reg = re.compile(reg_str)

	# Sets up url for detectron http server, default is local host
	host, port = '127.0.0.1', '665'
	url = f'http://{host}:{port}'

	# Creates output dir
	num_path, fname = os.path.split(list(gt_dict.keys())[0])
	data_dir, num_dir = os.path.split(num_path)
	mask_dir = os.path.join(data_dir, 'masks')
	if not os.path.exists(mask_dir):
		os.makedirs(mask_dir)

	# Goes through all rgb images in gt dict
	gt_dict_masks = {}
	mask_missed = []
	for path_rgb, rec_dict in gt_dict.items():
		# Opens rgb image in bgr
		frame = cv2.imread(path_rgb, -1)

		# [vis.png, bbList, labelList, scoreList, maskList]
		retList = upload(url, frame)

		# If mask found
		if retList:
			#DEBUG Shows vis img
			if DEBUG:
				visImg = retList[0]
				visImg = cv2.resize(visImg, (1200, 900))
				cv2.imshow('Inference', visImg)
				k = cv2.waitKey(1)
				if k == 27:
					cv2.destroyAllWindows()
					break 

			# Gets mask list
			maskList = retList[-1]
			bbList = retList[1]
			gt_dict_masks.update({
				path_rgb : {
					'pos'  : rec_dict['pos'],
					'neg'  : rec_dict['neg'],
					'mask' : maskList,
					'bb'   : bbList
				}

			})

			# Gets rgb image number for output masks
			num_path, fname = os.path.split(path_rgb)
			fnum = reg.match(fname).group(1)

			# Writes vis file
			img_vis = retList[0]
			fname_vis = f'pred{fnum}maskvis.png'
			path_vis = os.path.join(mask_dir, fname_vis)
			cv2.imwrite(path_vis, img_vis)

			# Goes through all the masks
			for count, mask in enumerate(maskList):
				mask[mask > 0] = 255
				fname_mask = f'pred{fnum}mask{str(count).zfill(2)}.png'
				path_mask = os.path.join(mask_dir, fname_mask)
				cv2.imwrite(path_mask, mask)

		# If not mask found, stores missed
		else:
			mask_missed.append(path_rgb)

	# Returns mask dict and missed masks
	return (gt_dict_masks, mask_missed)

# Main function, needs at least dataset directory path
def main(dataset_dir_path, vis_dir_path=None, incl_negs=False):
	# Gets all rgb png paths
	path_list_rgb = get_rgb_paths(dataset_dir_path)

	# Gets all neg/pos rectange files
	path_list_pos, path_list_neg = get_rec_paths(dataset_dir_path)

	# Create ground truth dict
	gt_dict = make_gt_dict(path_list_rgb, path_list_pos, path_list_neg)
	
	# If vis
	if vis_dir_path:
		create_vis(vis_dir_path, gt_dict, incl_negs)

	# Creates masks if true
	mask = True
	# If masks, gets masks and missed masks
	if mask:
		gt_dict_masks, mask_missed = create_masks(gt_dict)
		for mask in mask_missed:
			print(mask)

	# If not masks, just reg gt dict
	else: 
		gt_dict_masks = gt_dict

	# Returns gt_dict, with/without masks
	return gt_dict_masks, mask_missed

# If main file, gets cli args
if __name__ == '__main__':
	# Args, main dataset path and vis output path
	incl_negs = False
	dataset_dir_path = sys.argv[1]
	if len(sys.argv) > 2:
		vis_dir_path = sys.argv[2]
		if len(sys.argv) > 3:
			incl_negs = True
	else: vis_dir_path = None

	# Runs main
	main(dataset_dir_path, vis_dir_path, incl_negs)