# To implement:
# Will have to implement a time tracker so that we can call in the time that bounding box + id combos have been present. If it has reached a certain threshold
# we can conclude that it is a lego piece (a consistent contour). We will then take a photo of that piece at different time intervals and put it into our model

import math
import uuid
import random

class EuclideanDistTracker:
    def __init__(self):
        # Store the center positions of the objects
        self.center_points = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.id_count = 0
        self.createdUniqueIds = []


    def update(self, objects_rect):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            same_object_detected = False
            # Find out if that object was detected already
            for id, pttime in self.center_points.items():
                xpoint = pttime[0][0]
                ypoint = pttime[0][1]
                timerVal = pttime[1]
                uniqueId = pttime[2]
                dist = math.hypot(cx - xpoint, cy - ypoint)

                if dist < 50:
                    self.center_points[id] = [(cx, cy), timerVal+1, uniqueId]
                    objects_bbs_ids.append([x, y, w, h, id, timerVal+1, uniqueId])
                    same_object_detected = True
                    break

            # New object is detected we assign the ID to that object
            if same_object_detected is False:
                #print("a new piece detected")
                #print("current unique ids are", self.createdUniqueIds)
                
                uniqueId = str(uuid.UUID(int=random.getrandbits(128), version=4))
                
                while(uniqueId in self.createdUniqueIds):
                    uniqueId = str(uuid.UUID(int=random.getrandbits(128), version=4))
                #print("unqiue id generating for this one", uniqueId)
                
                self.createdUniqueIds.append(uniqueId)

                self.center_points[self.id_count] = [(cx, cy), 0, uniqueId]
                objects_bbs_ids.append([x, y, w, h, self.id_count, 0, uniqueId])
                self.id_count += 1

        # Clean the dictionary by center points to remove IDS not used anymore
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            object_id = obj_bb_id[4]
            center = self.center_points[object_id][0]
            timeAlive = self.center_points[object_id][1]
            object_unique_id = self.center_points[object_id][2]
            new_center_points[object_id] = [center, timeAlive, object_unique_id]

        # Update dictionary with IDs not used removed
        self.center_points = new_center_points.copy()
        # print(objects_bbs_ids)
        return objects_bbs_ids



