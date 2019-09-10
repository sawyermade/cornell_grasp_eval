import os, sys, re, json, cv2, math

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
			files_rgb.sort(key=lambda x: int(reg.match(x).group(1)))
			path_list += [os.path.join(root, f) for f in files_rgb]

	# Sorts by dir number 01-10 and returns
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
			files_pos.sort(key=lambda x: int(reg_pos.match(x).group(1)))
			files_neg.sort(key=lambda x: int(reg_neg.match(x).group(1)))
			path_list_pos += [os.path.join(root, f) for f in files_pos]
			path_list_neg += [os.path.join(root, f) for f in files_neg]

	# Sorts by dir number 01-10 and returns
	path_list_pos.sort(key=lambda x: int(x.split(os.sep)[-2]))
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

''' Makes ground truth dictionary, 
key is rgb file path and contains dicts for pos/neg keys with 3d list of rectangle points'''
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

	return gt_dict

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