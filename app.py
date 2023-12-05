from flask import Flask, render_template, request
import pyodbc
app = Flask(__name__)
connection_string = 'DRIVER={SQL Server};SERVER=devwn11023;DATABASE=master;Trusted_Connection=yes;'
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/log_services')
def form():
    return render_template('log_services.html')
@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    where_col_value = request.form['where_col_value']
    like_query_value = request.form['like_query_value']
    date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    from_datetime = date + " " + start_time
    to_datetime = date + " " + end_time
    # message = ""
    if like_query_value == "":
        message = like_query_value
    else:
        message = "%" + like_query_value + "%"
    # Connect to the SQL Server using Windows Authentication
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM IDOODS.LogServices.Log with (nolock) WHERE (CreatedDate BETWEEN ? AND ?) AND (Message LIKE ? OR commonidentifier = ?)",
                   from_datetime, to_datetime, message, where_col_value)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    # You could pass the data to another template to display it
    return render_template('log_results.html', data=data)

@app.route('/jmh_details')
def jmhform():
    return render_template('jmh_details.html')
@app.route('/jmh_submit', methods=['POST'])
def jmh_submit():
    jmhid = request.form['jmhid']
    jhm_list = jmhid.split(',')
    jhm_list =  [x.strip() for x in jhm_list]
    jmhids = ','.join('?' for unused in jhm_list)
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM IDOJMH.JMH.JobExecution with (nolock) WHERE JobID IN ({jmhids})",
                   jhm_list)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('jmh_results.html', data=data)

@app.route('/mft_details')
def mftform():
    return render_template('mft_details.html')
@app.route('/mft_submit', methods=['POST'])
def mft_submit():
    mft_id = request.form['mftid']
    mft_list = mft_id.split(',')
    mft_list = [x.strip() for x in mft_list]
    mfts = ','.join('?' for unused in mft_list)
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute(f"SELECT JobHeaderInternalID,MFTID,JobName,JobDescription,SourceName,SourcePath,SourceExpression,Targetname,targetPath,TargetFileNameExpression FROM IDOServices.MFT.vJobs with (nolock) where MFTID IN ({mfts})",mft_list)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('mft_results.html', data=data)

@app.route('/session_details')
def sessionform():
    return render_template('session_details.html')
@app.route('/session_submit', methods=['POST'])
def session_submit():
    session_id = request.form['sessionname']
    session_list = session_id.split(',')
    session_list = [x.strip() for x in session_list]
    sessions = ','.join('?' for unused in session_list)
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute(f"SELECT top (15) A.WORKFLOWNAME,D.* FROM [IDOETL].[WFCONTROL].[WORKFLOW] as A ,[IDOETL].[WFCONTROL].[PROCESS] as B,[IDOJobReporting].[JOBREPORTING].[JOB] as C,[IDOJobReporting].[JOBREPORTING].[JOBDETAIL] as D with (nolock) WHERE  A.PROCESSID=B.PROCESSID AND C.PROCESSID = B.JOBREPORTINGPROCESSID AND C.JOBID  = D.JOBID AND C.RESULTCODE <>'s' AND A.WORKFLOWNAME  IN ({sessions}) order by lastupdated desc", session_list)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('session_results.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)