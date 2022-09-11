// Helper function used for validation purposes of emails
const validateEmail = (email) => {
  return String(email).toLowerCase().match(
    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  );
};


document.addEventListener('DOMContentLoaded', function () {
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email(undefined));

  // Register an event listener to listen for user inputs. Prevent submitting an empty form
  document.querySelector('#compose-recipients').onkeyup = () => {
    if (document.querySelector('#compose-recipients').value.length > 0) {
      document.querySelector('#compose-button').disabled = false;
    } else {
      document.querySelector('#compose-button').disabled = true;
    }
  }

  // Make POST request to submit new emails
  document.querySelector('#compose-form').onsubmit = () => {
    // Retrieve payload values and get rid of the white inside the list of recipients
    const recipients = document.querySelector('#compose-recipients').value.replace(/\s/g, "");
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    // Prevent from submitting empty mail
    if (recipients.length === 0 || subject.length === 0 || body.length === 0) {
      return false;
    }

    // Check if emails of recipients are valid
    recipients.split(',').forEach(email => {
      if (!validateEmail(email).includes(email)) {
        return false;
      }
    });

    // Make POST request
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients,
        subject,
        body
      })
    })
      .then(response => response.json())
      .then(result => {
        // Print result
        console.log(result);
        load_mailbox('sent');
      });

    // Prevent default behavior
    return false;
  }

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email(email) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // If it's a reply to an incoming emails, prefill composition fields, otherwise clear out composition fields
  document.querySelector('#compose-recipients').value = email ? email.sender : '';
  // If it's a reply, attach 'Re: ' before the subject, otherwise if it's a reply to a reply (hence the subject already contains 'Re: '), leave as it is
  document.querySelector('#compose-subject').value = email ? (email.subject.includes('Re:') ? email.subject : 'Re: ' + email.subject) : '';
  // Add an indication of the content of the original email body
  document.querySelector('#compose-body').value = email ? 'On ' + email.timestamp + ' ' + email.sender + ' wrote: ' + email.body + '\n' : '';

  // Enable submit button, if it's a reply with pre-filled composition fields
  if (email)
    document.querySelector('#compose-button').disabled = false;
}


function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch all emails in user's inbox, outbox and archive
  fetch('/emails/' + mailbox)
    .then(response => response.json())
    .then(emails => {
      const ul = document.createElement('ul');
      ul.className = 'list-group';

      // Create list element for each email and attach it to unordered list
      emails.forEach(email => {
        console.log(email);

        const li = document.createElement('li');
        li.className = "list-group-item";
        li.setAttribute('aria-current', 'true');
        // Register an event handler to toggle css styling for inbox email element when hovered
        li.onmouseenter = () => li.classList.add('list-group-item-action', 'active');
        // Register an event handle to remove css styling for inbox email element when no longer hovered
        li.onmouseleave = () => li.classList.remove('list-group-item-action', 'active');
        // Display email content once clicked
        li.onclick = () => display_email(email, mailbox);

        const a = document.createElement('a');
        a.setAttribute('href', '#');

        const div = document.createElement('div');
        div.className = 'd-flex w-100 justify-content-between';

        const heading = document.createElement('h5');
        heading.className = 'mb-1';
        // Display sender for inbox, otherwise display recipients for outbox view
        heading.innerHTML = (mailbox === 'sent') ? email.recipients.join(', ') : email.sender;
        div.append(heading);

        const small = document.createElement('small');
        small.innerHTML = email.timestamp;
        div.append(small);
        a.append(div);

        const paragraph = document.createElement('p');
        paragraph.className = 'mb-1';
        paragraph.innerHTML = email.subject;
        a.append(paragraph);

        // Apply specific styling, if the email has already been read (visual cue to tell unread emails from read)
        if (email.read)
          li.classList.add('unread');

        li.append(a);
        ul.append(li);
      });

      document.querySelector('#emails-view').append(ul);
    });
}


function display_email(mail, mailbox) {
  // I don't really see a reason here to make a specific endpoint, since the email contents could be passed as a parameter to this function
  // Nonetheless I am using fetch here to make use of an endpoint

  // Show the email and hide other views
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Remove all child nodes of the view to prevent it from displaying old emails user didn't click on
  document.querySelector('#email-view').innerHTML = '';

  // Fetch the email content using it's id
  fetch('/emails/' + mail.id)
    .then(response => response.json())
    .then(email => {
      // Print email
      console.log(email);

      const div = document.createElement('div');

      let heading = document.createElement('h5');
      heading.innerHTML = '<b>From:</b> ' + email.sender;
      div.append(heading);

      heading = document.createElement('h5');
      heading.innerHTML = '<b>To:</b> ' + email.recipients.join(', ');
      div.append(heading);

      heading = document.createElement('h5');
      heading.innerHTML = '<b>Subject:</b> ' + email.subject;
      div.append(heading);

      heading = document.createElement('h5');
      heading.innerHTML = '<b>Timestamp:</b> ' + email.timestamp;
      div.append(heading);

      if (mailbox !== 'sent') {
        let button = document.createElement('button');
        button.className = "btn btn-sm btn-outline-primary";
        button.id = "archive";
        button.innerHTML = email.archived ? "Unarchive" : "Archive";

        // Set an event handler to archive/unarchive an email if button has been clicked
        button.onclick = () => {
          fetch('/emails/' + email.id, {
            method: 'PUT',
            body: JSON.stringify({
              archived: email.archived ? false : true
            })
          })
            .then(response => load_mailbox('inbox'))
        }
        
        div.append(button);

        button = document.createElement('button');
        button.className = "btn btn-sm btn-outline-primary";
        button.id = "reply";
        button.innerHTML = "Reply";

        // Set an event handler to reply to incoming emails if the button has been clicked
        button.onclick = () => {
          compose_email(email);
        }

        div.append(button);
      }

      div.append(document.createElement('hr'));

      const paragraph = document.createElement('p');
      paragraph.innerHTML = email.body;
      div.append(paragraph);

      document.querySelector('#email-view').append(div);

      // Mark email as read, since user viewed it's content
      if (!email.read) {
        fetch('/emails/' + email.id, {
          method: 'PUT',
          body: JSON.stringify({
            read: true
          })
        })
      }
    });
}
