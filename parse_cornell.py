import os, sys, re, json, cv2, math

def get_rgb_paths(dataset_dir_path):
	# rgb filename regex
	reg_str = r'^pcd(\d{4})r\.png$'
	reg = re.compile(reg_str)

	# Goes through dirs
	path_list = []
	for root, dirs, files in os.walk(dataset_dir_path):
		# Gets all rgb images and sorts by image number
		if files:
			files = [f for f in files if reg.match(f)]
			files.sort(key=lambda x: int(reg.match(x).group(1)))
			path_list += [os.path.join(root, f) for f in files]

	# Sorts by dir number 01-10 and returns
	path_list.sort(key=lambda x: int(x.split(os.sep)[-2]))
	return path_list

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

def make_gt_dict(path_list_rgb, path_list_pos, path_list_neg):
	# Goes through all rgb/recs
	gt_dict = {}
	for path_rgb, path_pos, path_neg in zip(path_list_rgb, path_list_pos, path_list_neg):
		# Opens rec files
		pos_rec_list, neg_rec_list = [], []
		with open(path_pos) as posf, open(path_neg) as negf:
			# Goes through positive points
			rec_pts = []
			for num, line in enumerate(posf):
				# Gets point
				line_split = line.strip('\n').strip(' ').split(' ')
				point = tuple([float(p) for p in line_split])
				rec_pts.append(point)

				# Checks if new rectangle or not
				if num != 0 and (num+1) % 4 == 0:
					# Adds rectangle to list if no NaNs, cleas for new rec
					nan_flag = False
					for ps in rec_pts:
						for p in ps:
							if math.isnan(p):
								nan_flag = True
								break
						if nan_flag:
							break

					if not nan_flag:
						pos_rec_list.append(rec_pts)
					rec_pts = []

			# Goes through negative points
			rec_pts = []
			for num, line in enumerate(negf):
				# Gets point
				line_split = line.strip('\n').strip(' ').split(' ')
				point = tuple([float(p) for p in line_split])
				rec_pts.append(point)

				# Checks if new rectangle or not
				if num != 0 and (num+1) % 4 == 0:
					# Adds rectangle to list if no NaNs, cleas for new rec
					nan_flag = False
					for ps in rec_pts:
						for p in ps:
							if math.isnan(p):
								nan_flag = True
								break
						if nan_flag:
							break

					if not nan_flag:
						neg_rec_list.append(rec_pts)
					rec_pts = []

		# Adds to gt_dict
		gt_dict.update({
			path_rgb : {
				'pos' : pos_rec_list,
				'neg' : neg_rec_list
			}
		})

	# Returns ground truth dictionary
	return gt_dict

def create_vis(vis_dir_path, gt_dict):
	# rgb filename regex
	reg_str = r'^pcd(\d{4})r\.png$'
	reg = re.compile(reg_str)

	# Goes through rgb images
	for rgb_path, rec_dict in gt_dict.items():
		# Opens image
		img = cv2.imread(rgb_path, -1)

		# Draws pos recs
		color = (0, 255, 0)
		for rec in rec_dict['pos']:
			if len(rec) < 4: print(rgb_path, rec)
			p1, p2, p3, p4 = [(round(r[0]), round(r[1])) for r in rec]
			cv2.line(img, p1, p2, color)
			cv2.line(img, p2, p3, color)
			cv2.line(img, p3, p4, color)
			cv2.line(img, p4, p1, color)

		# Draws neg recs
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

def main(dataset_dir_path, vis_dir_path):
	# Gets all rgb png paths
	path_list_rgb = get_rgb_paths(dataset_dir_path)

	# Gets all neg/pos rectange files
	path_list_pos, path_list_neg = get_rec_paths(dataset_dir_path)

	# Create ground truth dict
	gt_dict = make_gt_dict(path_list_rgb, path_list_pos, path_list_neg)
	
	# If vis
	if vis_dir_path:
		create_vis(vis_dir_path, gt_dict)

	return gt_dict

if __name__ == '__main__':
	# Args, main dataset path and vis output path
	dataset_dir_path = sys.argv[1]
	if len(sys.argv) > 2:
		vis_dir_path = sys.argv[2]
	else: vis_dir_path = None

	# Runs main
	main(dataset_dir_path, vis_dir_path)