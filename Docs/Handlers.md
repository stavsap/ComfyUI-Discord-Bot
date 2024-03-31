# Workflow Handlers

TODO

# Nodes required for integration

The following nodes are a must for workflow that is handled by a handler.

## SaveImageWebsocket

This node should input the final images of the workflow, sending images to this node will result in images to be published by the bot back to the user.

![pic](../.meta/save-to-socket-node.png)

# Built In Handlers

## Text 2 Image

Simple basic workflow that not requires any additional extra custom nodes.


## Image 2 Image

Basic image to image workflow.

Requires: https://github.com/glowcone/comfyui-load-image-from-url custom node to be able to load images from urls.