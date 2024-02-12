import mset
import os

class QuickBakerSetupPlugin:
    """
    Creates A Baker Project
    - Add A project name( bake and texture project will be named this)
    - Add Quick Loader Mesh of Low and High Poly
    - Add texture Output path
    - Select Texture Size
    """

    projectWidth = 0
    projectHeight = 0
    padding = 8

    window = mset.UIWindow("Quick Baker Setup")
    pathMeshTextUI = mset.UITextField()
    pathtextureTextUI = mset.UITextField()
    nameTextureTextUI = mset.UITextField()
    projectNameTextUI = mset.UITextField()
    textureSizeListUI = mset.UIListBox()
    useMeshMaterialCBUI = mset.UICheckBox()
    useMultiUVSetCBUI = mset.UICheckBox()
    
    #Setup UI
    def setup_ui(self) -> None:
        nameText = mset.UILabel("Project Name")
        self.window.addElement(nameText)

        self.window.addReturn()

        self.window.addElement(self.projectNameTextUI)

        self.window.addReturn()

        ## Output Section
        meshLabel = mset.UILabel("Add Quick Loader Mesh")
        self.window.addElement(meshLabel)

        self.window.addReturn()
        #mesh path textUI
        self.window.addElement( self.pathMeshTextUI)
        #mesh button open dialog box
        meshButton = mset.UIButton("Select Mesh")
        meshButton.onClick = lambda: self.getMeshByDialog()
        self.window.addElement(meshButton)

        self.window.addReturn()
        self.window.addReturn()

        textureLabel = mset.UILabel("Texture Output")
        self.window.addElement(textureLabel)

        self.window.addReturn()
        self.window.addReturn()

        # add path Texture TextUI
        self.window.addElement(self.pathtextureTextUI)

        textureButton = mset.UIButton("Texture Output")
        textureButton.onClick = lambda: self.getTextureByDialog()
        self.window.addElement(textureButton)
        self.textureSizeListUI.title = "Project Size"
        self.textureSizeListUI.addItem("256")
        self.textureSizeListUI.addItem("512")
        self.textureSizeListUI.addItem("1024")
        self.textureSizeListUI.addItem("2048")
        self.textureSizeListUI.addItem("4096")
        self.textureSizeListUI.onSelect = lambda: self.getSelectedListBox()
        self.window.addReturn()

        self.window.addElement(self.textureSizeListUI)
        self.window.addReturn()

        self.window.addElement(self.useMeshMaterialCBUI)
        self.useMeshMaterialCBUI.label = "Use Mesh Material"
        self.window.addReturn()

        self.window.addElement(self.useMultiUVSetCBUI)
        self.useMultiUVSetCBUI.label = "Enable Multiple UV Sets"
        self.window.addReturn()

        bakeButton = mset.UIButton("Bake")
        bakeButton.onClick = lambda: self.startBake()
        self.window.addElement(bakeButton)

        closeButton = mset.UIButton("Close")
        closeButton.onClick = mset.shutdownPlugin
        self.window.addElement(closeButton)

    # create baking project
    def createBakeProject(self):

        if not self.projectNameTextUI.value:
            mset.err("Need project name.\n")
            return
        
        if not self.pathMeshTextUI.value:
            mset.err("Need mesh path.\n")
            return
        
        if not self.pathtextureTextUI.value:
            mset.err("Need texture path.\n")
            return
        
        if self.projectHeight == 0:
            mset.err("Project size not specified.\n")
            return
        
        if self.projectWidth == 0:
            mset.err("Project size not specified.\n")
            return
        

        bakerObj = mset.BakerObject()
        bakerObj.name = self.projectNameTextUI.value + "BakeProject"
        bakerObj.importModel(self.pathMeshTextUI.value)
        bakerObj.outputPath = self.pathtextureTextUI.value + self.projectNameTextUI.value + ".tga"
        bakerObj.outputBits = 8
        bakerObj.outputSamples = 16
        bakerObj.edgePadding = "Moderate"
        bakerObj.edgePaddingSize = self.padding
        bakerObj.outputSoften = 0
        bakerObj.useHiddenMeshes = False
        bakerObj.ignoreTransforms = False
        bakerObj.smoothCage = True
        bakerObj.ignoreBackfaces = True
        bakerObj.multipleTextureSets = self.useMultiUVSetCBUI.value

        bakerObj.outputHeight = self.projectHeight
        bakerObj.outputWidth = self.projectWidth

        normalMap = bakerObj.getMap("Normals")
        normalMap.enabled = True
        normalMap.flipX = True

        curvMap = bakerObj.getMap("Curvature")
        curvMap.enabled = True
        curvMap.dither = True
        curvMap.strength = 1.0

        AOMap = bakerObj.getMap("Ambient Occlusion")
        AOMap.enabled = True

        MatMap = bakerObj.getMap("Material ID")
        MatMap.enabled = True

        positionMap = bakerObj.getMap("Position")
        positionMap.enabled = True
        
        #baker output
        if not self.useMultiUVSetCBUI.value:
            print("Create single Texture Project")
            textureProject = self.createTextureProject()
            print(bakerObj.linkTextureProject("",textureProject))
        else:
            print("Create multiple Texture Project")
            for i in range(bakerObj.getTextureSetCount()):
                textureProject = self.createTextureProject()
                texName = bakerObj.getTextureSetName(i)
                #name of texture set
                print(texName)
                textureProject.name = textureProject.name + "_" + texName
                textureProject.addLinkedMaterial(mset.findMaterial(texName))
                #issues with linking texture project with baker object
                bakerObj.linkTextureProject(texName,textureProject)

        bakerObj.savePreset("MyQuickSetup")
        bakerObj.bake()


    def createTextureProject(self) -> None:
        textureProject = mset.TextureProjectObject()
        textureProject.name = self.projectNameTextUI.value + "TextureProject"
        textureProject.projectWidth = self.projectWidth
        textureProject.projectHeight = self.projectHeight
        textureProject.paddingSize = self.padding
        textureProject.outputPath = self.pathtextureTextUI.value
        textureProject.outputPathBaseName = self.projectNameTextUI.value
        textureProject.addProjectMap("albedo")
        textureProject.addProjectMap("normal")
        textureProject.addProjectMap("metalness")
        textureProject.addProjectMap("roughness")
        textureProject.addProjectMap("bump")
        textureProject.addProjectMap("ambient occlusion")
        textureProject.useBumpAsDetailNormals = True
        if not self.useMeshMaterialCBUI.value:
            mat = mset.Material()
            mat.name = self.projectNameTextUI.value + "_mat"
            textureProject.addLinkedMaterial(mat)
        
        #Change Your Output maps
        # textureProject.addOutputMap("_albedo", "RGB","TGA",8,"Albedo","Metalness")
        # textureProject.addOutputMap("_normal", "RGB+A","TGA",8,"Normal","Metalness")
        # mixmap = textureProject.addOutputMap("_ARM", "R+G+B","TGA",8,"mixmap","Metalness")
        # mixmap.r = "Ambient Occluison"
        # mixmap.g = "Roughness"
        # mixmap.b = "Metalness"
        return textureProject

    def startBake(self):
        self.createBakeProject()

    # open dialogbox and add to mesh path
    def getMeshByDialog(self):
        paths = mset.showOpenFileDialog(fileTypes=['fbx'], multiple=False)
        self.pathMeshTextUI.value = paths
        print(self.pathMeshTextUI.value)
    
    # open dialogbox and add to mesh path
    def getTextureByDialog(self):
        path = mset.showOpenFolderDialog()
        self.pathtextureTextUI.value = path + "/"
        print(self.pathtextureTextUI.value)

    #Sets projects maps height and width
    def getSelectedListBox(self) -> None:
        selectedSize = self.textureSizeListUI.selectedItem
        if selectedSize == 0:
            selectedSize = 256
        elif selectedSize == 1:
            selectedSize = 512
        elif selectedSize == 2:
            selectedSize = 1024
        elif selectedSize == 3:
            selectedSize = 2048
        elif selectedSize == 4:
            selectedSize = 4096

        self.projectHeight = selectedSize
        self.projectWidth = selectedSize

    def __init__(self):
        """
        Starts the plugin.
        """
        self.setup_ui()
        self.window.visible = True


# Start the Plugin by generating the UI
if __name__ == '__main__':
    QuickBakerSetupPlugin()