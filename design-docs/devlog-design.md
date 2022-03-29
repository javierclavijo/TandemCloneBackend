`10/03/2022`

I've decided to start with the visual design for the app. This is my basic idea for it:

1. The design will be mostly based on the real Tandem app, accounting for the differences the project has from it.
2. The color palette will be simple:
    - White, for backgrounds
    - Dark grey text
    - Lighter gray as a secondary color
    - Blue or green as a primary color
    - Orange or similar as the accent color
3. The design will be mobile-first, to be adapted to desktop later.

So there we go. My main tasks now are:

- [x] Investigate the Tandem app to get inspiration for the design.
    - [x] Make screenshots where needed, e.g. register flow.
- [x] Decide the color palette with coolors
- [x] Decide which fonts I'm going to use
- [ ] Create mobile wireframes, then desktop
- [ ] Create *desktop* design, *then* mobile

Edit: just by writing the app, I've realised that the way I'm handling user interests is too rigid. Tandem seems to
simply store them as a string. I'll change that in the backend, it really doesn't make much sense for it to be an enum.
I could even remove it entirely and use the user description string instead, perhaps making it a JSON field. I've also
forgotten the profile photo field, but well, that shouldn't be too hard.

I've also tried to join Tandem, but they say that they must review all applications, etc. It's pretty restrictive. Also,
I don't think they'll accept it, as I apparently didn't send my profile photo. So, at least meanwhile, I'll have to
design on my own. It can't be too hard --just make a social media app and add a chat.

Anyway, the views I'll need at the very list are these:

- General
    - [x] Landing
    - [x] Sign up flow
    - [x] Homepage/my profile
    - [x] Edit profile
- Chat
    - [x] Chat
    - [x] User (chat) detail
    - [x] Channel (chat) detail
    - [x] Channel chat detail
    - [x] Channel edit
- Community
    - [x] User list
    - [x] Channel list

Color palette: I'm considering the following options (I'd add white and grey, of course):
https://coolors.co/1f1f1f-e3e3e3-ffffff-ff595e-ffca3a-8ac926-1982c4-6a4c93
https://coolors.co/1f1f1f-e3e3e3-ffffff-9b5de5-f15bb5-fee440-00bbf9-00f5d4
https://coolors.co/1f1f1f-e3e3e3-ffffff-8ecae6-219ebc-023047-ffb703-fb8500
I think it's better to make the wireframes, choose one of these to make the design and try the other ones too.

Fonts:

- Decorative: Quicksand... Maybe Bungee, if I can make a suitable icon...?
- Paragraphs, etc.: Rubik?

Icons: Iconoir

`11/03/2022`

Designing wireframes from the ground up is being a bit tough, but so far so good. I've made most of the wireframes with
a decent amount of detail. Hopefully I'll be able to make the first version of the design soon. Then, I think the best
course of action is start making the frontend and make adjustments to the design and backend as needed.

On the topic of search, I'm definitely going to simplify it as much as possible. There will be a search box to find
users and channels by name and description (interests, which I've decided to store as a string, or JSON with a couple of
fields). Languages should be decided according to the user's profile, and should be selectable. Language levels should
probably be filterable by the user --you may want to search only users according to their level in your native language,
or perhaps you don't care about their level, etc.

Edit: I've finished drawing all the wireframes. I'm really satisfied with the result, and I look forward to start
drawing the first mockups. There aren't any blatant gaps in the wireframes, everything has a purpose and every screen is
well-defined --unlike my website for the design/frontend courses, hehe. I probably won't be able to do more today,
though.

`14/03/2022`

It's been a couple of days since I last wrote an entry here, but I've kept working on the wireframes. Of course, I had
forgotten about the desktop wireframes last time... But well, they're mostly done. My aim for today is finishing them as
fast as I can, to start with the desktop designs as soon as possible.

Going mobile first with the design was definitely a wise decision: the desktop views are mostly composed of the mobile
ones --sometimes combined to fill space and provide a more fluid user experience-- and the 'transition' from mobile to
desktop is a lot more 'logical' than the reverse as the mobile layouts are usually forced by necessity to be simple.

In the end, I've resorted to, ***ahem***, getting very inspired by the Whatsapp interface, especially for the desktop
mockups. The result so far is turning out very well, I deem. The 'social' features will probably be very light (the home
and search screens) and their design will be simple.

As I went from mobile to desktop in the wireframes, I will do the reverse in the first version of the design. This is
due to the fact that I've made some changes going from mobile to desktop, which I'd like to add to the mobile design.

So there we go, I'll write something later as usual.

Edit: so, I was able to finish the wireframes pretty quickly.

I'm getting the user profile pictures from https://randomuser.me/photos --according to their license, usage is allowed
in mockups.

`16/03/2022`

Progress has indeed slowed down lately, but there are some things on the bright side. I've discovered the Figma
auto-layout and component variants workflows, which will definitely allow me to design a lot faster, as they allow
components to behave like flex containers (sort of) and be interchangeable. I'll spend more time configuring the
components, but it will save me a lot of time moving things around, updating and resizing them.

Channel detail photo -- https://unsplash.com/photos/G5ZenftPPOA

`19/03/2022`

User detail photo -- https://unsplash.com/photos/bncaoYSyfns (needed a higher res photo)

`21/03/2022`

Other channel detail photos:

- https://unsplash.com/photos/z7bgxD7NTxA
- https://unsplash.com/photos/I3hr1j192Mo
- https://unsplash.com/photos/xztaR1fBI84
- https://unsplash.com/photos/ZvUD8Wzyfgs
- https://unsplash.com/photos/IOXlfr7_3oE
- https://unsplash.com/photos/hFif4ha5Dfk
- https://unsplash.com/photos/Q5IO7kum-J8

`22/03/2022`

Another option for the site's color palette: https://coolors.co/333333-f7f7f7-f76464-7e22ce
Another one: https://coolors.co/333333-f7f7f7-c6b1fc-7b64c0-534097
This one is really good, might be the definitive: https://coolors.co/333333-ffffff-c4b0fd-7b64c0-473781-ff9776

`27/03/2022`

I'm almost there with the design. There are only a few things to do before I start coding the frontend. Overall, I think
the end result is turning out rather nice, although it will surely need some adjustments --in fact, I have some in mind
already. My plan, however, is to finish the design quickly and to start coding the frontend as soon as possible --even
if I make the adjustments now, I don't want the design phase to drag any longer. It's being mostly pleasant and a nice
learning experience, but I definitely prefer coding. I hope that I can finish it tomorrow. For now, I'll just review it
and write down what I still have to do in the Figma project.   