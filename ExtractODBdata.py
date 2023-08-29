'''
Created by nnkrishnan at Kappa Lab, IITH
'''


import csv
import json
import numpy
from abaqus import *
from abaqusConstants import *


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


# def main():
odbFileName = 'ODBname.odb'
assemblyInstanceName = 'Assembly-name'
stepName = 'Step-1'
surfaceOfNodes = 'My-set-name'
fieldVariableName = 'U'

currentODB = session.openOdb(name=odbFileName)
currentRootAssembly = currentODB.rootAssembly
currentStep = currentODB.steps[stepName]
listOfFrames = currentStep.frames
noOfAvailableFrames = len(listOfFrames)

nodeSetOfSurface = currentRootAssembly.nodeSets[surfaceOfNodes].nodes[0]

listOfNodesIndexOnSurface = []
listOfNodesCoordinatesOnSurface = []

print("start capturing nodes on surface")

nodeOnSurfaceList = []
for node, i in zip(nodeSetOfSurface, range(0, len(nodeSetOfSurface))):
    listOfNodesIndexOnSurface.append(node.label - 1)
    listOfNodesCoordinatesOnSurface.append(
        (node.coordinates[0], node.coordinates[1], node.coordinates[2]))
    nodeObj = {
        "x": json.dumps(node.coordinates[0], cls=MyEncoder),
        "y": json.dumps(node.coordinates[1], cls=MyEncoder),
        "z": json.dumps(node.coordinates[2], cls=MyEncoder),
        "label": node.label,
        "indexInSet": i
    }
    nodeOnSurfaceList.append(nodeObj)

nodeOnSurfaceJSON = json.dumps(nodeOnSurfaceList)
with open("nodeData.json", "w") as outfile:
    outfile.write(nodeOnSurfaceJSON)

print "end capturing nodes on surface"

listOfFramesProcessed =[]
for currentFrame, i in zip(listOfFrames, range(0, (len(listOfFrames)))):
    if(i % 500 == 0 or i == 627 or i == 411):
        print('Querying nodes for Frame.... ', currentFrame.frameId)
        nodeDataList = []
        for nodeData,node in zip(nodeOnSurfaceList,nodeSetOfSurface):
            fieldForFrameAtNode = currentFrame.fieldOutputs[fieldVariableName].getSubset(region=node)

            u1 = json.dumps(fieldForFrameAtNode.values[1].data[0], cls=MyEncoder)
            u2 = json.dumps(fieldForFrameAtNode.values[1].data[1], cls=MyEncoder)
            u3 = json.dumps(fieldForFrameAtNode.values[1].data[2], cls=MyEncoder)
            nodeObj = {
                "initialX": nodeData["x"],
                "initialY": nodeData["y"],
                "initialZ": nodeData["z"],
                "label": nodeData["label"],
                "frameId": currentFrame.frameId,
                "frameValue": currentFrame.frameValue,
                "u1": str(u1),
                "u2": str(u2),
                "u3": str(u3),
                "finalX": str(float(nodeData["x"]) + float(u1)),
                "finalY": str(float(nodeData["y"]) + float(u2)),
                "finalZ": str(float(nodeData["z"]) + float(u3)),

            }
            nodeDataList.append(nodeObj)
        listOfFramesProcessed.append([currentFrame.frameId])
        dataPoint = {
            "frameId": currentFrame.frameId,
            "frameValue": currentFrame.frameValue,
            "nodeData": nodeDataList
        }
        dataPointJSON = json.dumps(dataPoint)
        print ('writing Frame Data for ',currentFrame.frameId,' to JSON')
        with open("FrameData"+str(i)+".json", "w") as outfile:
            outfile.write(dataPointJSON)
        print ('JSON for ',currentFrame.frameId,'th frame saved ....')
    else:
        continue

with open('ListOfProcessedFrames' +'.csv', 'wb') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(listOfFramesProcessed)


print('End.................')


# if __name__ == '__main__':
#     main()
