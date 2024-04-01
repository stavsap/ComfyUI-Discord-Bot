# User Guide

To interact with the Bot, there is a need to use '/' commands.

Just type '/' and you should be able to see the list of all commands under you Bot name.

## Commands List

### /q {message}

Queue a workflow of the current handler with a given message. The message should contain all the required information and syntax for the current handler. 

To make efficient prompting without the need to deal with long repeating prompts check the [handler-context](#handler-context) command to set prefix or postfix and [refs](#ref-set-ref-value) features.

The message will be processed by appending a prefix if set to the beginning of the message then appending the postfix if set to the end of the message, then the message`s refs will be replaced with their corresponding value.

### /q-status

View the current queue information, the running and the pending prompt ids.

### /ref-set {ref} {value}

Will set a reference to a given string value under the given ref-name. This will be set as #<ref-name> and if present in the **/q** {message}, will be replaced with the corresponding value.

<details>
  <summary>Example</summary>

/ref-set 'config' '--res 1024:768 --cfg 5 --steps 40'

Will result in

```shell
#config=--res 1024:768 --cfg 5 --steps 40
```

and the /q message is

```shell
a robot #config
```

will result in message

```shell
a robot --res 1024:768 --cfg 5 --steps 40
```

</details>

The refs are stored per handler.

**restrictions**: the given ref-name can`t include '#' char or white spaces!.

### /ref-del {ref}

Remove a certain ref by name. 

**restrictions**: the given ref-name cant include '#' char or white spaces!.

### /ref-view 

View all current ref tuples.

### /handlers

View all supported handler, the list is buttons, pressing a button will set the current handler as selected.

### /handler-info

View information regarding the current selected workflow handler.

### /handler-context

Set and View the handler constant context. Upon submit all data will be persisted per handler.

the final message that will be constructed to be passed to the handler as follows:

{**Flags**}{**Prefix**}`{/q meesage}`{**Postfix**}

#### Prefix

This will set a constant prefix that will be appended to the beginning of the submitted message when using the /q {message} command.

#### Postfix

This will set a constant Postfix that will be appended to the end of  submitted message when using the /q {message} command.

#### Flags

This will set the flags for the handler (can be any other text), the flags section will be appended to the begging of the message after the prefix is appended, resulting that the flags are the first to parse, so other section can override their values if present.

<details>
  <summary>Example</summary>

![pic](../.meta/handler-context.png)

</details>

### /checkpoints

View all the checkpoints currently set in comfy server.

## Uploading Images

Uploading any images to the bot will result in corresponding ordered url links for the image. this urls can be used for workloads that can load image via url.