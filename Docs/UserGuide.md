# User Guide

To interact with the Bot, there is a need to use '/' commands.

Just type '/' and you should be able to see the list of all commands under you Bot name.

## Commands List

### /q {message}

Queue a workflow of the current handler with a given message. The message should contain all the required information and syntax for the current handler.

### /ref-set {ref} {value}

Will set a reference to a given string value under the given ref-name. This will be set as #<ref-name> and if present in the **/q** {message}, will be replaced with the corresponding value.

For example:

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

The refs are stored per handler.

restrictions: the ref-name cant include '#' char or white spaces!.

### /ref-del {ref}

Remove a certain ref by name. 

restrictions: the ref-name cant include '#' char or white spaces!.

### /ref-view 

View all current ref tuples.

### /prefix {prefix}

This will append a constant prefix in the beginning of a given message, prefix can include ref #`s and they will be handled accordingly. 

The prefix is stored per handler.

### /prefix-del

Will remove the current prefix if any set.

### /prefix-view 

Will display the current prefix if any set.

### /postfix {postfix}

This will append a constant postfix in the end of a given message, postfix can include ref #`s and they will be handled accordingly. 

The postfix is stored per handler.

### /postfix-del

Will remove the current postfix if any set.

### /postfix-view 

Will display the current postfix if any set.

### /info

TODO describe

### /checkpoints

View all the checkpoints currently set in comfy server.

### /handlers

View all supported handler, the list is buttons, pressing a button will set the current handler as selected.

### /q-status

View the current queue information and the running and the pending prompt ids.

## Uploading Images

TODO