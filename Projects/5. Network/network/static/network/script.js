document.addEventListener('DOMContentLoaded', () => {


    const newPost = document.querySelector('#post-text');

    if (newPost) {
        // Event listner to toggle on/off submit button
        newPost.onkeyup = () => {
            if (newPost.value.length > 0) {
                document.querySelector('#post-button').disabled = false;
            } else {
                document.querySelector('#post-button').disabled = true;
            }
        }
    }


    // Generates an array removing the first element from NodeList containing list group items (first element is an element used to add new posts)
    [].slice.call(document.querySelectorAll('.list-group-item'), 1).forEach(item => {

        if (item.querySelector('#post-like-tracker')) {
            const likeButton = item.querySelector('#post-like-tracker').querySelector('#post-like-btn');

            // Event listener to like/unlike a post
            likeButton.onclick = () => {
                const post_id = item.querySelector('#post-id').innerHTML;
                const user_id = item.querySelector('#user-id').innerHTML;

                // Register a like from given user
                fetch('/posts/like', {
                    method: 'PUT',
                    body: JSON.stringify({
                        post_id,
                        user_id
                    })
                })
                    // Then refresh likes count
                    .then(response => response.json())
                    .then(data => {
                        if (!data.error)
                            item.querySelector('#post-like-tracker').querySelector('#post-likes').innerHTML = data.likes
                    })
            }
        }


        const editButton = item.querySelector('#post-edit-btn');

        if (editButton) {
            // Event listener to edit post's content
            editButton.onclick = () => {
                const content = item.querySelector('#post-content-view');
                const edit = item.querySelector('#post-content-edit-view');
                const textarea = item.querySelector('#post-content-edit');
                const paragraph = item.querySelector('#post-content');

                // Toggle on/off display property, depending if editButton has been pressed again or not
                if (content.style.display === 'none') {
                    editButton.innerHTML = 'Edit';
                    content.style.display = 'block';
                    edit.style.display = 'none';

                    // Fetch to edit post content
                    fetch('/posts/edit/' + item.querySelector('#post-id').innerHTML, {
                        method: 'PUT',
                        body: JSON.stringify({
                            content: textarea.value
                        })
                    })
                        // Refresh too see updated post content
                        .then(response => {
                            if (response.status !== 403)
                                paragraph.innerHTML = textarea.value;

                            textarea.value = '';   
                        })
                } else {
                    editButton.innerHTML = 'Save'
                    content.style.display = 'none';
                    edit.style.display = 'block';
                    textarea.value = paragraph.innerHTML;
                }
            }
        }
    })
});


// Follow/unfollow given user, sends POST request to create follow entity and DELETE request to remove it
const follow = () => {
    const button = document.querySelector('#profile-btn');

    fetch(button.innerHTML === 'Follow' ? '/follow' : '/unfollow', {
        method: button.innerHTML === 'Follow' ? 'POST' : 'DELETE',
        body: JSON.stringify({
            user_id: document.querySelector('#author-id').innerHTML
        })
    })
        .then(response => response.json())
        .then(data => {
            document.querySelector('#followers').innerHTML = `<strong>${data.followers}</strong>`;
            button.innerHTML = button.innerHTML === 'Follow' ? 'Unfollow' : 'Follow'
        })
}
